from __future__ import annotations

from typing import Optional, List, Union, cast, NamedTuple

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.common import int_from_hex
from starknet_py.constants import DEFAULT_DEPLOYER_ADDRESS
from starknet_py.net.client_models import Hash, Call
from starknet_py.net.models import AddressRepresentation, parse_address, compute_address
from starknet_py.utils.contructor_args_translator import translate_constructor_args
from starknet_py.utils.crypto.facade import pedersen_hash
from starknet_py.utils.data_transformer.universal_deployer_serializer import (
    universal_deployer_serializer,
    deploy_contract_abi,
)
from starknet_py.utils.sync import add_sync_methods


ContractDeployment = NamedTuple("ContractDeployment", [("udc", Call), ("address", int)])


@add_sync_methods
class Deployer:
    """
    Deployer used to deploy contracts through Universal Deployer Contract (UDC)
    """

    def __init__(
        self,
        *,
        deployer_address: AddressRepresentation = DEFAULT_DEPLOYER_ADDRESS,
        account_address: Optional[AddressRepresentation] = None,
    ):
        """
        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on real nets and devnet) by default.
            Must be set when using custom network other than devnet.
        :param account_address: Address of an account which will send the transaction.
            If passed, address of the contract to be deployed will be connected with it.
        """

        self.deployer_address = parse_address(deployer_address)
        self.account_address = account_address
        self.unique = account_address is not None

    async def create_deployment_call(
        self,
        class_hash: Hash,
        *,
        salt: Optional[int] = None,
        abi: Optional[List] = None,
        calldata: Optional[Union[List, dict]] = None,
    ) -> ContractDeployment:
        """
        Creates deployment call to the UDC contract

        :param class_hash: The class_hash of the contract to be deployed
        :param salt: The salt for a contract to be deployed. Random value is selected if it is not provided
        :param abi: ABI of the contract to be deployed
        :param calldata: Constructor args of the contract to be deployed
        :return: NamedTuple with call and address of the contract to be deployed
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
        salt = pedersen_hash(self.account_address, salt) if self.unique else salt
        address = compute_address(
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            salt=salt,
            deployer_address=deployer_address,
        )

        return ContractDeployment(udc=call, address=address)
