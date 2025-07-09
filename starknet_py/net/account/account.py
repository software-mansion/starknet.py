import dataclasses
from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.constants import (
    ANY_CALLER,
    FEE_CONTRACT_ADDRESS,
    QUERY_VERSION_BASE,
    OutsideExecutionInterfaceID,
)
from starknet_py.hash.address import compute_address
from starknet_py.hash.outside_execution import outside_execution_to_typed_data
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.utils import verify_message_signature
from starknet_py.net.account.account_deployment_result import AccountDeploymentResult
from starknet_py.net.account.base_account import (
    BaseAccount,
    OutsideExecutionSupportBaseMixin,
)
from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    Call,
    Calls,
    EstimatedFee,
    Hash,
    OutsideExecution,
    OutsideExecutionTimeBounds,
    ResourceBoundsMapping,
    SentTransactionResponse,
    SierraContractClass,
    Tag,
)
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import AddressRepresentation, parse_address
from starknet_py.net.models.chains import RECOGNIZED_CHAIN_IDS, Chain, parse_chain
from starknet_py.net.models.transaction import (
    AccountTransaction,
    DeclareV3,
    DeployAccountV3,
    InvokeV3,
    TypeAccountTransaction,
)
from starknet_py.net.models.typed_data import TypedDataDict
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.serialization.data_serializers import (
    ArraySerializer,
    FeltSerializer,
    PayloadSerializer,
    StructSerializer,
    UintSerializer,
)
from starknet_py.utils.iterable import ensure_iterable
from starknet_py.utils.sync import add_sync_methods
from starknet_py.utils.typed_data import TypedData


# pylint: disable=too-many-public-methods,disable=too-many-lines
@add_sync_methods
class Account(BaseAccount, OutsideExecutionSupportBaseMixin):
    """
    Default Account implementation.
    """

    ESTIMATED_FEE_MULTIPLIER: float = 1.5
    """Amount by which each estimated fee is multiplied when using `auto_estimate`."""

    ESTIMATED_AMOUNT_MULTIPLIER: float = 1.5
    ESTIMATED_UNIT_PRICE_MULTIPLIER: float = 1.5
    """Values by which each estimated `max_amount` and `max_price_per_unit` are multiplied when using 
    `auto_estimate`. Used only for V3 transactions"""

    def __init__(
        self,
        *,
        address: AddressRepresentation,
        client: Client,
        signer: Optional[BaseSigner] = None,
        key_pair: Optional[KeyPair] = None,
        chain: Optional[Chain] = None,
    ):
        """
        :param address: Address of the account contract.
        :param client: Instance of Client which will be used to add transactions.
        :param signer: Custom signer to be used by Account.
                       If none is provided, default
                       :py:class:`starknet_py.net.signer.stark_curve_signer.StarkCurveSigner` is used.
        :param key_pair: Key pair that will be used to create a default `Signer`.
        :param chain: Chain ID associated with the account.
            This can be supplied in multiple formats:

            - an enum :py:class:`starknet_py.net.models.StarknetChainId`
            - a string name (e.g. 'SN_SEPOLIA')
            - a hexadecimal value (e.g. '0x1')
            - an integer (e.g. 1)
        """
        self._address = parse_address(address)
        self._client = client
        self._cairo_version = None
        self._chain_id = None if chain is None else parse_chain(chain)

        if signer is not None and key_pair is not None:
            raise ValueError("Arguments signer and key_pair are mutually exclusive.")

        if signer is None:
            if key_pair is None:
                raise ValueError(
                    "Either a signer or a key_pair must be provided in Account constructor."
                )
            if self._chain_id is None:
                raise ValueError("One of chain or signer must be provided.")

            signer = StarkCurveSigner(
                account_address=self.address, key_pair=key_pair, chain_id=self._chain_id
            )
        self.signer: BaseSigner = signer

    @property
    def address(self) -> int:
        return self._address

    @property
    async def cairo_version(self) -> int:
        if self._cairo_version is None:
            assert isinstance(self._client, FullNodeClient)
            contract_class = await self._client.get_class_at(
                contract_address=self._address
            )
            self._cairo_version = (
                1 if isinstance(contract_class, SierraContractClass) else 0
            )
        return self._cairo_version

    @property
    def client(self) -> Client:
        return self._client

    async def _get_resource_bounds(
        self,
        transaction: AccountTransaction,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
    ) -> ResourceBoundsMapping:
        if auto_estimate and resource_bounds is not None:
            raise ValueError(
                "Arguments auto_estimate and resource_bounds are mutually exclusive."
            )

        if auto_estimate:
            estimated_fee = await self.estimate_fee(transaction)
            assert isinstance(estimated_fee, EstimatedFee)

            return estimated_fee.to_resource_bounds()

        if resource_bounds is None:
            raise ValueError(
                "One of arguments: resource_bounds or auto_estimate must be specified when invoking a transaction."
            )

        return resource_bounds

    async def _prepare_invoke_v3(
        self,
        calls: Calls,
        *,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        nonce: Optional[int] = None,
        auto_estimate: bool = False,
        tip: int,
    ) -> InvokeV3:
        """
        Takes calls and creates InvokeV3 from them.

        :param calls: Single call or a list of calls.
        :param resource_bounds: Resource limits (L1 and L2) that can be used in this transaction.
        :param auto_estimate: Use automatic fee estimation; not recommended as it may lead to high costs.
        :return: InvokeV3 created from the calls (without the signature).
        """
        if nonce is None:
            nonce = await self.get_nonce()

        wrapped_calldata = _parse_calls(await self.cairo_version, calls)

        transaction = InvokeV3(
            calldata=wrapped_calldata,
            resource_bounds=ResourceBoundsMapping.init_with_zeros(),
            signature=[],
            nonce=nonce,
            sender_address=self.address,
            version=3,
            tip=tip,
        )

        resource_bounds = await self._get_resource_bounds(
            transaction, resource_bounds, auto_estimate
        )
        return _add_resource_bounds_to_transaction(transaction, resource_bounds)

    async def estimate_fee(
        self,
        tx: Union[AccountTransaction, List[AccountTransaction]],
        skip_validate: bool = False,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> Union[EstimatedFee, List[EstimatedFee]]:
        transactions = (
            await self.sign_for_fee_estimate(tx)
            if isinstance(tx, AccountTransaction)
            else [await self.sign_for_fee_estimate(t) for t in tx]
        )

        return await self._client.estimate_fee(
            tx=transactions,
            skip_validate=skip_validate,
            block_hash=block_hash,
            block_number=block_number,
        )

    async def get_nonce(
        self,
        *,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        Get the current nonce of the account.

        :param block_hash: Block's hash or literals `"pre_confirmed"` or `"latest"`
        :param block_number: Block's number or literals `"pre_confirmed"` or `"latest"`
        :return: nonce.
        """
        return await self._client.get_contract_nonce(
            self.address, block_hash=block_hash, block_number=block_number
        )

    async def _check_outside_execution_nonce(
        self,
        nonce: int,
        *,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> bool:
        (is_valid,) = await self._client.call_contract(
            call=Call(
                to_addr=self.address,
                selector=get_selector_from_name("is_valid_outside_execution_nonce"),
                calldata=[nonce],
            ),
            block_hash=block_hash,
            block_number=block_number,
        )
        return bool(is_valid)

    async def get_outside_execution_nonce(self, retry_count=10) -> int:
        while retry_count > 0:
            random_stark_address = KeyPair.generate().public_key
            if await self._check_outside_execution_nonce(random_stark_address):
                return random_stark_address
            retry_count -= 1
        raise RuntimeError("Failed to generate a valid nonce")

    async def _get_outside_execution_version(
        self,
    ) -> Union[OutsideExecutionInterfaceID, None]:
        for version in [
            OutsideExecutionInterfaceID.V1,
            OutsideExecutionInterfaceID.V2,
        ]:
            if await self.supports_interface(version):
                return version
        return None

    async def supports_interface(
        self, interface_id: OutsideExecutionInterfaceID
    ) -> bool:
        (does_support,) = await self._client.call_contract(
            Call(
                to_addr=self.address,
                selector=get_selector_from_name("supports_interface"),
                calldata=[interface_id],
            )
        )
        return bool(does_support)

    async def get_balance(
        self,
        token_address: Optional[AddressRepresentation] = None,
        *,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        if token_address is None:
            chain_id = await self._get_chain_id()
            if chain_id in RECOGNIZED_CHAIN_IDS:
                token_address = FEE_CONTRACT_ADDRESS
            else:
                raise ValueError(
                    "Argument token_address must be specified when using a custom network."
                )

        low, high = await self._client.call_contract(
            Call(
                to_addr=parse_address(token_address),
                selector=get_selector_from_name("balance_of"),
                calldata=[self.address],
            ),
            block_hash=block_hash,
            block_number=block_number,
        )

        return (high << 128) + low

    async def sign_for_fee_estimate(
        self, transaction: TypeAccountTransaction
    ) -> TypeAccountTransaction:
        version = transaction.version + QUERY_VERSION_BASE
        transaction = dataclasses.replace(transaction, version=version)

        signature = self.signer.sign_transaction(transaction)
        return _add_signature_to_transaction(tx=transaction, signature=signature)

    async def sign_outside_execution_call(
        self,
        calls: Calls,
        execution_time_bounds: OutsideExecutionTimeBounds,
        *,
        caller: AddressRepresentation = ANY_CALLER,
        nonce: Optional[int] = None,
        interface_version: Optional[OutsideExecutionInterfaceID] = None,
    ) -> Call:
        if interface_version is None:
            interface_version = await self._get_outside_execution_version()

        if interface_version is None:
            raise RuntimeError(
                "Can't initiate call, outside execution is not supported."
            )

        if nonce is None:
            nonce = await self.get_outside_execution_nonce()

        outside_execution = OutsideExecution(
            caller=parse_address(caller),
            nonce=nonce,
            execute_after=execution_time_bounds.execute_after_timestamp,
            execute_before=execution_time_bounds.execute_before_timestamp,
            calls=list(ensure_iterable(calls)),
        )
        chain_id = await self._get_chain_id()
        signature = self.signer.sign_message(
            outside_execution_to_typed_data(
                outside_execution, interface_version, chain_id
            ),
            self.address,
        )
        selector_for_version = {
            OutsideExecutionInterfaceID.V1: "execute_from_outside",
            OutsideExecutionInterfaceID.V2: "execute_from_outside_v2",
        }

        return Call(
            to_addr=self.address,
            selector=get_selector_from_name(selector_for_version[interface_version]),
            calldata=_outside_transaction_serialiser.serialize(
                {
                    "outside_execution": outside_execution.to_abi_dict(),
                    "signature": signature,
                }
            ),
        )

    async def sign_invoke_v3(
        self,
        calls: Calls,
        *,
        nonce: Optional[int] = None,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        tip: int = 0,
    ) -> InvokeV3:
        invoke_tx = await self._prepare_invoke_v3(
            calls,
            resource_bounds=resource_bounds,
            nonce=nonce,
            auto_estimate=auto_estimate,
            tip=tip,
        )
        signature = self.signer.sign_transaction(invoke_tx)
        return _add_signature_to_transaction(invoke_tx, signature)

    async def sign_declare_v3(
        self,
        compiled_contract: str,
        compiled_class_hash: int,
        *,
        nonce: Optional[int] = None,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        tip: int = 0,
    ) -> DeclareV3:
        # pylint: disable=too-many-arguments
        declare_tx = await self._make_declare_v3_transaction(
            compiled_contract,
            compiled_class_hash,
            nonce=nonce,
            tip=tip,
        )
        resource_bounds = await self._get_resource_bounds(
            declare_tx, resource_bounds, auto_estimate
        )
        declare_tx = _add_resource_bounds_to_transaction(declare_tx, resource_bounds)

        signature = self.signer.sign_transaction(declare_tx)
        return _add_signature_to_transaction(declare_tx, signature)

    async def _make_declare_v3_transaction(
        self,
        compiled_contract: str,
        compiled_class_hash: int,
        *,
        nonce: Optional[int] = None,
        tip: int,
    ) -> DeclareV3:
        contract_class = create_sierra_compiled_contract(
            compiled_contract=compiled_contract
        )

        if nonce is None:
            nonce = await self.get_nonce()

        declare_tx = DeclareV3(
            contract_class=contract_class.convert_to_sierra_contract_class(),
            compiled_class_hash=compiled_class_hash,
            sender_address=self.address,
            signature=[],
            nonce=nonce,
            version=3,
            resource_bounds=ResourceBoundsMapping.init_with_zeros(),
            tip=tip,
        )
        return declare_tx

    async def sign_deploy_account_v3(
        self,
        class_hash: int,
        contract_address_salt: int,
        *,
        constructor_calldata: Optional[List[int]] = None,
        nonce: int = 0,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        tip: int = 0,
    ) -> DeployAccountV3:
        # pylint: disable=too-many-arguments
        deploy_account_tx = DeployAccountV3(
            class_hash=class_hash,
            contract_address_salt=contract_address_salt,
            constructor_calldata=(constructor_calldata or []),
            version=3,
            resource_bounds=ResourceBoundsMapping.init_with_zeros(),
            signature=[],
            nonce=nonce,
            tip=tip,
        )
        resource_bounds = await self._get_resource_bounds(
            deploy_account_tx, resource_bounds, auto_estimate
        )
        deploy_account_tx = _add_resource_bounds_to_transaction(
            deploy_account_tx, resource_bounds
        )

        signature = self.signer.sign_transaction(deploy_account_tx)
        return _add_signature_to_transaction(deploy_account_tx, signature)

    async def execute_v3(
        self,
        calls: Calls,
        *,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        nonce: Optional[int] = None,
        auto_estimate: bool = False,
        tip: int = 0,
    ) -> SentTransactionResponse:
        execute_transaction = await self.sign_invoke_v3(
            calls,
            nonce=nonce,
            resource_bounds=resource_bounds,
            auto_estimate=auto_estimate,
            tip=tip,
        )
        return await self._client.send_transaction(execute_transaction)

    def sign_message(self, typed_data: Union[TypedData, TypedDataDict]) -> List[int]:
        if isinstance(typed_data, TypedData):
            return self.signer.sign_message(typed_data, self.address)
        typed_data_dataclass = TypedData.from_dict(typed_data)
        return self.signer.sign_message(typed_data_dataclass, self.address)

    def verify_message(
        self, typed_data: Union[TypedData, TypedDataDict], signature: List[int]
    ) -> bool:
        if not isinstance(typed_data, TypedData):
            typed_data = TypedData.from_dict(typed_data)
        message_hash = typed_data.message_hash(account_address=self.address)
        return verify_message_signature(message_hash, signature, self.signer.public_key)

    @staticmethod
    async def deploy_account_v3(
        *,
        address: AddressRepresentation,
        class_hash: int,
        salt: int,
        key_pair: KeyPair,
        client: Client,
        constructor_calldata: Optional[List[int]] = None,
        nonce: int = 0,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        tip: int = 0,
    ) -> AccountDeploymentResult:
        # pylint: disable=too-many-arguments, too-many-locals

        """
        Deploys an account contract with provided class_hash on Starknet and returns
        an AccountDeploymentResult that allows waiting for transaction acceptance.

        Provided address must be first prefunded with enough tokens, otherwise the method will fail.

        :param address: Calculated and prefunded address of the new account.
        :param class_hash: Class hash of the account contract to be deployed.
        :param salt: Salt used to calculate the address.
        :param key_pair: KeyPair used to calculate address and sign deploy account transaction.
        :param client: Client instance used for deployment.
        :param constructor_calldata: Optional calldata to account contract constructor. If ``None`` is passed,
            ``[key_pair.public_key]`` will be used as calldata.
        :param nonce: Nonce of the transaction.
        :param resource_bounds: Resource limits (L1 and L2) used when executing this transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param tip: The tip amount to be added to the transaction fee.
        """
        calldata = (
            constructor_calldata
            if constructor_calldata is not None
            else [key_pair.public_key]
        )

        chain = await client.get_chain_id()

        account = _prepare_account_to_deploy(
            address=address,
            class_hash=class_hash,
            salt=salt,
            key_pair=key_pair,
            client=client,
            chain=chain,
            calldata=calldata,
        )

        deploy_account_tx = await account.sign_deploy_account_v3(
            class_hash=class_hash,
            contract_address_salt=salt,
            constructor_calldata=calldata,
            nonce=nonce,
            resource_bounds=resource_bounds,
            auto_estimate=auto_estimate,
            tip=tip,
        )

        result = await client.deploy_account(deploy_account_tx)

        return AccountDeploymentResult(
            hash=result.transaction_hash, account=account, _client=account.client
        )

    async def _get_chain_id(self) -> int:
        if self._chain_id is None:
            chain = await self._client.get_chain_id()
            self._chain_id = parse_chain(chain)

        return self._chain_id


def _prepare_account_to_deploy(
    address: AddressRepresentation,
    class_hash: int,
    salt: int,
    key_pair: KeyPair,
    client: Client,
    chain: Chain,
    calldata: List[int],
) -> Account:
    # pylint: disable=too-many-arguments
    address = parse_address(address)

    if address != (
        computed := compute_address(
            salt=salt,
            class_hash=class_hash,
            constructor_calldata=calldata,
            deployer_address=0,
        )
    ):
        raise ValueError(
            f"Provided address {hex(address)} is different than computed address {hex(computed)} "
            f"for the given class_hash and salt."
        )

    return Account(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=chain,
    )


def _is_sierra_contract(data: Dict[str, Any]) -> bool:
    return "sierra_program" in data


def _add_signature_to_transaction(
    tx: TypeAccountTransaction, signature: List[int]
) -> TypeAccountTransaction:
    return dataclasses.replace(tx, signature=signature)


def _add_max_fee_to_transaction(
    tx: TypeAccountTransaction, max_fee: int
) -> TypeAccountTransaction:
    return dataclasses.replace(tx, max_fee=max_fee)


def _add_resource_bounds_to_transaction(
    tx: TypeAccountTransaction, resource_bounds: ResourceBoundsMapping
) -> TypeAccountTransaction:
    return dataclasses.replace(tx, resource_bounds=resource_bounds)


def _parse_calls(cairo_version: int, calls: Calls) -> List[int]:
    if cairo_version == 1:
        parsed_calls = _parse_calls_cairo_v1(ensure_iterable(calls))
        wrapped_calldata = _execute_payload_serializer_v1.serialize(
            {"calls": parsed_calls}
        )
    else:
        call_descriptions, calldata = _merge_calls(ensure_iterable(calls))
        wrapped_calldata = _execute_payload_serializer_v0.serialize(
            {"call_array": call_descriptions, "calldata": calldata}
        )
    return wrapped_calldata


def _parse_call_cairo_v0(call: Call, entire_calldata: List) -> Tuple[Dict, List]:
    _data = {
        "to": call.to_addr,
        "selector": call.selector,
        "data_offset": len(entire_calldata),
        "data_len": len(call.calldata),
    }
    entire_calldata += call.calldata

    return _data, entire_calldata


def _merge_calls(calls: Iterable[Call]) -> Tuple[List[Dict], List[int]]:
    call_descriptions = []
    entire_calldata = []
    for call in calls:
        data, entire_calldata = _parse_call_cairo_v0(call, entire_calldata)
        call_descriptions.append(data)

    return call_descriptions, entire_calldata


def _parse_calls_cairo_v1(calls: Iterable[Call]) -> List[Dict]:
    calls_parsed = []
    for call in calls:
        _data = {
            "to": call.to_addr,
            "selector": call.selector,
            "calldata": call.calldata,
        }
        calls_parsed.append(_data)

    return calls_parsed


_felt_serializer = FeltSerializer()
_call_description_cairo_v0 = StructSerializer(
    OrderedDict(
        to=_felt_serializer,
        selector=_felt_serializer,
        data_offset=_felt_serializer,
        data_len=_felt_serializer,
    )
)
_call_description_cairo_v1 = StructSerializer(
    OrderedDict(
        to=_felt_serializer,
        selector=_felt_serializer,
        calldata=ArraySerializer(_felt_serializer),
    )
)

_execute_payload_serializer_v0 = PayloadSerializer(
    OrderedDict(
        call_array=ArraySerializer(_call_description_cairo_v0),
        calldata=ArraySerializer(_felt_serializer),
    )
)
_execute_payload_serializer_v1 = PayloadSerializer(
    OrderedDict(
        calls=ArraySerializer(_call_description_cairo_v1),
    )
)
_outside_transaction_serialiser = StructSerializer(
    OrderedDict(
        outside_execution=StructSerializer(
            OrderedDict(
                caller=FeltSerializer(),
                nonce=FeltSerializer(),
                execute_after=UintSerializer(bits=64),
                execute_before=UintSerializer(bits=64),
                calls=ArraySerializer(_call_description_cairo_v1),
            )
        ),
        signature=ArraySerializer(FeltSerializer()),
    )
)
