import dataclasses
import re
from collections import OrderedDict
from typing import Dict, Iterable, List, Optional, Tuple, TypeVar, Union

from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.common import create_compiled_contract
from starknet_py.constants import QUERY_VERSION_BASE
from starknet_py.net import KeyPair
from starknet_py.net.account.account_deployment_result import AccountDeploymentResult
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    Call,
    Calls,
    Declare,
    EstimatedFee,
    Hash,
    Invoke,
    SentTransactionResponse,
    Tag,
)
from starknet_py.net.models import (
    AddressRepresentation,
    StarknetChainId,
    chain_from_network,
    compute_address,
    parse_address,
)
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.models.typed_data import TypedData
from starknet_py.net.networks import (
    MAINNET,
    TESTNET,
    TESTNET2,
    default_token_address_for_network,
)
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.serialization.data_serializers.array_serializer import ArraySerializer
from starknet_py.serialization.data_serializers.felt_serializer import FeltSerializer
from starknet_py.serialization.data_serializers.payload_serializer import (
    PayloadSerializer,
)
from starknet_py.serialization.data_serializers.struct_serializer import (
    StructSerializer,
)
from starknet_py.utils.iterable import ensure_iterable
from starknet_py.utils.sync import add_sync_methods
from starknet_py.utils.typed_data import TypedData as TypedDataDataclass


@add_sync_methods
class Account(BaseAccount):
    """
    Default Account implementation.
    """

    ESTIMATED_FEE_MULTIPLIER: float = 1.5
    """Amount by which each estimated fee is multiplied when using `auto_estimate`."""

    def __init__(
        self,
        *,
        address: AddressRepresentation,
        client: Client,
        signer: Optional[BaseSigner] = None,
        key_pair: Optional[KeyPair] = None,
        chain: Optional[StarknetChainId] = None,
    ):
        """
        :param address: Address of the account contract.
        :param client: Instance of Client which will be used to add transactions.
        :param signer: Custom signer to be used by Account.
                       If none is provided, default
                       :py:class:`starknet_py.net.signer.stark_curve_signer.StarkCurveSigner` is used.
        :param key_pair: Key pair that will be used to create a default `Signer`.
        :param chain: ChainId of the chain used to create the default signer.
        """
        if chain is None and signer is None:
            raise ValueError("One of chain or signer must be provided.")

        self._address = parse_address(address)
        self._client = client

        if signer is not None and key_pair is not None:
            raise ValueError("Arguments signer and key_pair are mutually exclusive.")

        if signer is None:
            if key_pair is None:
                raise ValueError(
                    "Either a signer or a key_pair must be provided in Account constructor."
                )

            chain = chain_from_network(net=client.net, chain=chain)
            signer = StarkCurveSigner(
                account_address=self.address, key_pair=key_pair, chain_id=chain
            )
        self.signer: BaseSigner = signer

    @property
    def address(self) -> int:
        return self._address

    @property
    def client(self) -> Client:
        return self._client

    @property
    def supported_transaction_version(self) -> int:
        return 1

    async def _get_max_fee(
        self,
        transaction: Union[Invoke, Declare, DeployAccount],
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> int:
        if auto_estimate and max_fee is not None:
            raise ValueError(
                "Arguments max_fee and auto_estimate are mutually exclusive."
            )

        if auto_estimate:
            estimate_fee = await self._estimate_fee(transaction)
            max_fee = int(estimate_fee.overall_fee * Account.ESTIMATED_FEE_MULTIPLIER)

        if max_fee is None:
            raise ValueError(
                "Argument max_fee must be specified when invoking a transaction."
            )

        return max_fee

    async def _prepare_invoke_function(
        self,
        calls: Calls,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Invoke:
        """
        Takes calls and creates Invoke from them.

        :param calls: Single call or list of calls.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Invoke created from the calls (without the signature).
        """
        nonce = await self.get_nonce()

        call_descriptions, calldata = _merge_calls(ensure_iterable(calls))
        wrapped_calldata = _execute_payload_serializer.serialize(
            {"call_array": call_descriptions, "calldata": calldata}
        )

        transaction = Invoke(
            calldata=wrapped_calldata,
            signature=[],
            max_fee=0,
            version=self.supported_transaction_version,
            nonce=nonce,
            contract_address=self.address,
        )

        max_fee = await self._get_max_fee(transaction, max_fee, auto_estimate)

        return _add_max_fee_to_transaction(transaction, max_fee)

    async def _verify_message_hash(self, msg_hash: int, signature: List[int]) -> bool:
        """
        Verify a signature of a given hash.

        :param msg_hash: hash to be verified.
        :param signature: signature of the hash.
        :return: true if the signature is valid, false otherwise.
        """
        calldata = [msg_hash, len(signature), *signature]

        call = Call(
            to_addr=self.address,
            selector=get_selector_from_name("is_valid_signature"),
            calldata=calldata,
        )
        try:
            await self._client.call_contract(call=call, block_hash="pending")
            return True
        except ClientError as ex:
            if re.search(r"Signature\s.+,\sis\sinvalid", ex.message):
                return False
            raise ex

    async def _estimate_fee(
        self,
        tx: Union[Invoke, Declare, DeployAccount],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> EstimatedFee:
        """
        :param tx: Transaction which fee we want to calculate.
        :param block_hash: a block hash.
        :param block_number: a block number.
        :return: Estimated fee.
        """
        tx = await self.sign_for_fee_estimate(tx)

        return await self._client.estimate_fee(
            tx=tx,
            block_hash=block_hash,
            block_number=block_number,
        )

    async def get_nonce(self) -> int:
        """
        Get the current nonce of the account.

        :return: nonce.
        """
        return await self._client.get_contract_nonce(
            self.address, block_number="pending"
        )

    async def get_balance(
        self, token_address: Optional[AddressRepresentation] = None
    ) -> int:
        token_address = token_address or default_token_address_for_network(
            self._client.net
        )

        low, high = await self._client.call_contract(
            Call(
                to_addr=parse_address(token_address),
                selector=get_selector_from_name("balanceOf"),
                calldata=[self.address],
            ),
            block_hash="pending",
        )

        return (high << 128) + low

    async def sign_for_fee_estimate(
        self, transaction: Union[Invoke, Declare, DeployAccount]
    ) -> Union[Invoke, Declare, DeployAccount]:
        version = self.supported_transaction_version + QUERY_VERSION_BASE
        transaction = dataclasses.replace(transaction, version=version)

        signature = self.signer.sign_transaction(transaction)
        return _add_signature_to_transaction(tx=transaction, signature=signature)

    async def sign_invoke_transaction(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Invoke:
        execute_tx = await self._prepare_invoke_function(calls, max_fee, auto_estimate)
        signature = self.signer.sign_transaction(execute_tx)
        return _add_signature_to_transaction(execute_tx, signature)

    async def sign_declare_transaction(
        self,
        compiled_contract: str,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Declare:
        compiled_contract = create_compiled_contract(
            compiled_contract=compiled_contract
        )
        declare_tx = Declare(
            contract_class=compiled_contract,
            sender_address=self.address,
            max_fee=0,
            signature=[],
            nonce=await self.get_nonce(),
            version=self.supported_transaction_version,
        )

        max_fee = await self._get_max_fee(
            transaction=declare_tx, max_fee=max_fee, auto_estimate=auto_estimate
        )
        declare_tx = _add_max_fee_to_transaction(declare_tx, max_fee)
        signature = self.signer.sign_transaction(declare_tx)
        return _add_signature_to_transaction(declare_tx, signature)

    async def sign_deploy_account_transaction(
        self,
        class_hash: int,
        contract_address_salt: int,
        constructor_calldata: Optional[List[int]] = None,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeployAccount:
        constructor_calldata = constructor_calldata or []

        deploy_account_tx = DeployAccount(
            class_hash=class_hash,
            contract_address_salt=contract_address_salt,
            constructor_calldata=constructor_calldata,
            version=self.supported_transaction_version,
            max_fee=0,
            signature=[],
            nonce=0,
        )

        max_fee = await self._get_max_fee(
            transaction=deploy_account_tx, max_fee=max_fee, auto_estimate=auto_estimate
        )
        deploy_account_tx = _add_max_fee_to_transaction(deploy_account_tx, max_fee)
        signature = self.signer.sign_transaction(deploy_account_tx)
        return _add_signature_to_transaction(deploy_account_tx, signature)

    async def execute(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> SentTransactionResponse:
        execute_transaction = await self.sign_invoke_transaction(
            calls, max_fee=max_fee, auto_estimate=auto_estimate
        )
        return await self._client.send_transaction(execute_transaction)

    def sign_message(self, typed_data: TypedData) -> List[int]:
        typed_data_dataclass = TypedDataDataclass.from_dict(typed_data)
        return self.signer.sign_message(typed_data_dataclass, self.address)

    async def verify_message(self, typed_data: TypedData, signature: List[int]) -> bool:
        typed_data_dataclass = TypedDataDataclass.from_dict(typed_data)
        message_hash = typed_data_dataclass.message_hash(account_address=self.address)
        return await self._verify_message_hash(message_hash, signature)

    @staticmethod
    async def deploy_account(
        *,
        address: AddressRepresentation,
        class_hash: int,
        salt: int,
        key_pair: KeyPair,
        client: Client,
        chain: StarknetChainId,
        constructor_calldata: Optional[List[int]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> AccountDeploymentResult:
        """
        Deploys an account contract with provided class_hash on StarkNet and returns
        an AccountDeploymentResult that allows waiting for transaction acceptance.

        Provided address must be first prefunded with enough tokens, otherwise the method will fail.

        If using Client for either TESTNET, TESTNET2 or MAINNET, this method will verify if the address balance
        is high enough to cover deployment costs.

        :param address: calculated and prefunded address of the new account.
        :param class_hash: class_hash of the account contract to be deployed.
        :param salt: salt used to calculate the address.
        :param key_pair: KeyPair used to calculate address and sign deploy account transaction.
        :param client: a Client instance used for deployment.
        :param chain: id of the StarkNet chain used.
        :param constructor_calldata: optional calldata to account contract constructor. If ``None`` is passed,
            ``[key_pair.public_key]`` will be used as calldata.
        :param max_fee: max fee to be paid for deployment, must be less or equal to the amount of tokens prefunded.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        """
        address = parse_address(address)
        calldata = (
            constructor_calldata
            if constructor_calldata is not None
            else [key_pair.public_key]
        )

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

        account = Account(
            address=address, client=client, key_pair=key_pair, chain=chain
        )

        deploy_account_tx = await account.sign_deploy_account_transaction(
            class_hash=class_hash,
            contract_address_salt=salt,
            constructor_calldata=calldata,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
        )

        if client.net in (TESTNET, TESTNET2, MAINNET):
            balance = await account.get_balance()
            if balance < deploy_account_tx.max_fee:
                raise ValueError(
                    "Not enough tokens at the specified address to cover deployment costs."
                )

        result = await client.deploy_account(deploy_account_tx)

        return AccountDeploymentResult(
            hash=result.transaction_hash, account=account, _client=account.client
        )


SignableTransaction = TypeVar("SignableTransaction", Invoke, Declare, DeployAccount)


def _add_signature_to_transaction(
    tx: SignableTransaction, signature: List[int]
) -> SignableTransaction:
    return dataclasses.replace(tx, signature=signature)


def _add_max_fee_to_transaction(
    tx: SignableTransaction, max_fee: int
) -> SignableTransaction:
    return dataclasses.replace(tx, max_fee=max_fee)


def _parse_call(call: Call, entire_calldata: List) -> Tuple[Dict, List]:
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
        data, entire_calldata = _parse_call(call, entire_calldata)
        call_descriptions.append(data)

    return call_descriptions, entire_calldata


_felt_serializer = FeltSerializer()
_call_description = StructSerializer(
    OrderedDict(
        to=_felt_serializer,
        selector=_felt_serializer,
        data_offset=_felt_serializer,
        data_len=_felt_serializer,
    )
)
_execute_payload_serializer = PayloadSerializer(
    OrderedDict(
        call_array=ArraySerializer(_call_description),
        calldata=ArraySerializer(_felt_serializer),
    )
)
