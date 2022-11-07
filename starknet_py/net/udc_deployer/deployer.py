from __future__ import annotations

from collections import namedtuple
from typing import Optional, List, Union, cast, NamedTuple

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.common import int_from_hex
from starknet_py.constants import DEFAULT_DEPLOYER_ADDRESS
from starknet_py.net import AccountClient
from starknet_py.net.client_models import Hash, InvokeFunction, Call
from starknet_py.net.models import AddressRepresentation, parse_address, compute_address
from starknet_py.utils.contructor_args_translator import translate_constructor_args
from starknet_py.utils.crypto.facade import pedersen_hash
from starknet_py.utils.data_transformer.universal_deployer_serializer import (
    universal_deployer_serializer,
    deploy_contract_abi,
)
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class Deployer:
    """
    Deployer used to deploy contracts through Universal Deployer Contract (UDC)
    """

    def __init__(
        self,
        account: AccountClient,
        *,
        deployer_address: AddressRepresentation = DEFAULT_DEPLOYER_ADDRESS,
        unique: bool = True,
    ):
        """
        :param account: AccountClient used to sign and send transactions
        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on real nets and devnet) by default.
            Must be set when using custom network other than devnet.
        :param unique: Boolean determining if the salt should be connected with the account's address. Default to True
        """

        self.account = account
        self.deployer_address = parse_address(deployer_address)
        self.unique = unique

    async def prepare_contract_deployment(
        self,
        *,
        class_hash: Hash,
        salt: Optional[int] = None,
        abi: Optional[List] = None,
        calldata: Optional[Union[List, dict]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeFunction:
        """
        Prepares deploy invoke transaction

        :param class_hash: The class_hash of the contract to be deployed
        :param salt: The salt for a contract to be deployed. Random value is selected if it is not provided
        :param abi: ABI of the contract to be deployed
        :param calldata: Constructor args of the contract to be deployed
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: NamedTuple with invoke_tx and address fields
        """
        call, address = await self.create_deployment_call(
            class_hash=class_hash, salt=salt, abi=abi, calldata=calldata
        )

        transaction = await self.account.sign_invoke_transaction(
            calls=call, max_fee=max_fee, auto_estimate=auto_estimate
        )

        return namedtuple(
            typename="InvokeAndAddress", field_names=["invoke_tx", "address"]
        )(transaction, address)

    async def create_deployment_call(
        self,
        *,
        class_hash: Hash,
        salt: Optional[int] = None,
        abi: Optional[List] = None,
        calldata: Optional[Union[List, dict]] = None,
    ) -> NamedTuple:
        """
        Creates deployment call to the UDC contract

        :param class_hash: The class_hash of the contract to be deployed
        :param salt: The salt for a contract to be deployed. Random value is selected if it is not provided
        :param abi: ABI of the contract to be deployed
        :param calldata: Constructor args of the contract to be deployed
        :return: NamedTuple with call and address fields
        """
        if not abi and calldata:
            raise ValueError("calldata was provided without an abi")

        salt = cast(int, salt or ContractAddressSalt.get_random_value())
        class_hash = int_from_hex(class_hash)

        constructor_calldata = translate_constructor_args(
            abi=abi or [], constructor_args=calldata
        )
        calldata, _ = universal_deployer_serializer.from_python(
            value_types=deploy_contract_abi["inputs"],
            classHash=class_hash,
            salt=salt,
            unique=int(self.unique),
            calldata=constructor_calldata,
        )

        call = Call(
            to_addr=self.deployer_address,
            selector=get_selector_from_name("deployContract"),
            calldata=calldata,
        )

        deployer_address = self.deployer_address if self.unique else 0
        salt = pedersen_hash(self.account.address, salt) if self.unique else salt
        address = compute_address(
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            salt=salt,
            deployer_address=deployer_address,
        )

        return namedtuple(typename="CallAndAddress", field_names=["call", "address"])(
            call, address
        )
