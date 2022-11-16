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
        :param account_address: Should be equal to the address of the account which will send the transaction.
            If passed, it will be used to modify the salt, otherwise, salt will not be affected.
        """

        self.deployer_address = parse_address(deployer_address)
        self.account_address = account_address
        self._unique = account_address is not None

    def create_deployment_call(
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

        raw_calldata = translate_constructor_args(
            abi=abi or [], constructor_args=calldata
        )

        return self.create_deployment_call_raw(
            class_hash=class_hash, salt=salt, raw_calldata=raw_calldata
        )

    def create_deployment_call_raw(
        self,
        class_hash: Hash,
        *,
        salt: Optional[int] = None,
        raw_calldata: Optional[List[int]] = None,
    ) -> ContractDeployment:
        """
        Creates deployment call to the UDC contract with plain Cairo calldata

        :param class_hash: The class_hash of the contract to be deployed
        :param salt: The salt for a contract to be deployed. Random value is selected if it is not provided
        :param raw_calldata: Plain Cairo constructor args of the contract to be deployed
        :return: NamedTuple with call and address of the contract to be deployed
        """
        salt = cast(int, salt or ContractAddressSalt.get_random_value())
        class_hash = int_from_hex(class_hash)

        calldata, _ = universal_deployer_serializer.from_python(
            value_types=deploy_contract_abi["inputs"],
            classHash=class_hash,
            salt=salt,
            unique=int(self._unique),
            calldata=raw_calldata or [],
        )

        call = Call(
            to_addr=self.deployer_address,
            selector=get_selector_from_name("deployContract"),
            calldata=calldata,
        )

        address = self._compute_address(salt, class_hash, raw_calldata or [])

        return ContractDeployment(udc=call, address=address)

    def _compute_address(
        self, salt: int, class_hash: int, constructor_calldata: List[int]
    ) -> int:
        deployer_address = self.deployer_address if self._unique else 0
        salt = (
            pedersen_hash(parse_address(self.account_address), salt)
            if self.account_address is not None
            else salt
        )
        return compute_address(
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            salt=salt,
            deployer_address=deployer_address,
        )
