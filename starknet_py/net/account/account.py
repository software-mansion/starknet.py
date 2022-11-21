import dataclasses
import re
from typing import Optional, Union, List, Iterable, Tuple, Dict, TypeVar

from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.common import create_compiled_contract
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net import KeyPair
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    Call,
    InvokeFunction,
    Declare,
    Calls,
    SentTransactionResponse,
    EstimatedFee,
    Hash,
    Tag,
)
from starknet_py.net.models import (
    AddressRepresentation,
    StarknetChainId,
    parse_address,
    chain_from_network,
)
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.networks import TESTNET, MAINNET
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.utils.data_transformer.execute_transformer import (
    execute_transformer_v1,
)
from starknet_py.utils.iterable import ensure_iterable
from starknet_py.net.models.typed_data import TypedData
from starknet_py.utils.typed_data import TypedData as TypedDataDataclass


class Account(BaseAccount):
    """
    Default Account implementation.
    """

    def __init__(
        self,
        *,
        address: AddressRepresentation,
        client: Client,
        signer: Optional[BaseSigner] = None,
        key_pair: Optional[KeyPair] = None,
        chain: Optional[StarknetChainId] = None,
    ):
        if chain is None and signer is None:
            raise ValueError("One of chain or signer must be provided")

        self.address = parse_address(address)
        self._client = client

        if signer is None:
            if key_pair is None:
                raise ValueError(
                    "Either a signer or a key_pair must be provided in AccountClient constructor"
                )

            chain = chain_from_network(net=client.net, chain=chain)
            signer = StarkCurveSigner(
                account_address=self.address, key_pair=key_pair, chain_id=chain
            )
        self.signer: BaseSigner = signer
        self._version = 1

    @property
    def client(self) -> Client:
        return self._client

    @property
    def supported_tx_version(self) -> int:
        return self._version

    def _get_default_token_address(self) -> str:
        if self._client.net not in [TESTNET, MAINNET]:
            raise ValueError(
                "Token_address must be specified when using a custom net address"
            )

        return FEE_CONTRACT_ADDRESS

    async def _get_max_fee(
        self,
        transaction: Union[InvokeFunction, Declare, DeployAccount],
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> int:
        if auto_estimate and max_fee is not None:
            raise ValueError(
                "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
            )

        if auto_estimate:
            estimate_fee = await self._estimate_fee(transaction)
            max_fee = int(estimate_fee.overall_fee * 1.1)

        if max_fee is None:
            raise ValueError("Max_fee must be specified when invoking a transaction")

        return max_fee

    async def _prepare_invoke_function(
        self,
        calls: Calls,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeFunction:
        """
        Takes calls and creates InvokeFunction from them

        :param calls: Single call or list of calls
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: InvokeFunction created from the calls (without the signature)
        """
        nonce = await self.get_nonce()

        calldata_py = _merge_calls(ensure_iterable(calls))
        wrapped_calldata, _ = execute_transformer_v1.from_python(*calldata_py)

        transaction = InvokeFunction(
            calldata=wrapped_calldata,
            signature=[],
            max_fee=0,
            version=self._version,
            nonce=nonce,
            contract_address=self.address,
        )

        max_fee = await self._get_max_fee(transaction, max_fee, auto_estimate)

        return _add_max_fee_to_transaction(transaction, max_fee)

    async def _verify_message_hash(self, msg_hash: int, signature: List[int]) -> bool:
        """
        Verify a signature of a given hash

        :param msg_hash: hash to be verified
        :param signature: signature of the hash
        :return: true if the signature is valid, false otherwise
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
        tx: Union[InvokeFunction, Declare, DeployAccount],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> EstimatedFee:
        """
        :param tx: Transaction which fee we want to calculate
        :return: Estimated fee
        """
        signature = self.signer.sign_transaction(tx)
        tx = _add_signature_to_transaction(tx, signature)

        return await self._client.estimate_fee(
            tx=tx,
            block_hash=block_hash,
            block_number=block_number,
        )

    async def get_nonce(self) -> int:
        """
        Get the current nonce of the account

        :return: nonce
        """
        return await self._client.get_contract_nonce(
            self.address, block_number="pending"
        )

    async def get_balance(
        self, token_address: Optional[AddressRepresentation] = None
    ) -> int:
        """
        Checks account's balance of specified token.

        :param token_address: Address of the ERC20 contract.
            If not specified it will be payment token (wrapped ETH) address.
        :return: Token balance
        """

        token_address = token_address or self._get_default_token_address()

        low, high = await self._client.call_contract(
            Call(
                to_addr=parse_address(token_address),
                selector=get_selector_from_name("balanceOf"),
                calldata=[self.address],
            ),
            block_hash="pending",
        )

        return (high << 128) + low

    async def sign_invoke_transaction(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeFunction:
        """
        Takes calls and creates signed InvokeFunction

        :param calls: Single call or list of calls
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: InvokeFunction created from the calls
        """

        execute_tx = await self._prepare_invoke_function(calls, max_fee, auto_estimate)
        signature = self.signer.sign_transaction(execute_tx)
        return _add_signature_to_transaction(execute_tx, signature)

    async def sign_declare_transaction(
        self,
        compiled_contract: str,
        *,
        cairo_path: Optional[List[str]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Declare:
        """
        Create and sign declare transaction.

        :param compiled_contract: string containing compiled contract bytecode.
                                  Useful for reading compiled contract from a file
        :param cairo_path: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: Signed Declare transaction
        """
        compiled_contract = create_compiled_contract(
            compiled_contract=compiled_contract, search_paths=cairo_path
        )
        declare_tx = Declare(
            contract_class=compiled_contract,
            sender_address=self.address,
            max_fee=0,
            signature=[],
            nonce=await self.get_nonce(),
            version=self._version,
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
        """
        Create and sign deploy account transaction

        :param class_hash: Class hash of the contract class to be deployed
        :param contract_address_salt: A salt used to calculate deployed contract address
        :param constructor_calldata: Calldata to be passed to contract constructor
            and used to calculate deployed contract address
        :param max_fee: Max fee to be paid for deploying account transaction. Enough tokens must be prefunded before
            sending the transaction for it to succeed.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: Signed DeployAccount transaction
        """
        constructor_calldata = constructor_calldata or []

        deploy_account_tx = DeployAccount(
            class_hash=class_hash,
            contract_address_salt=contract_address_salt,
            constructor_calldata=constructor_calldata,
            version=self._version,
            max_fee=0,
            signature=[],
            nonce=0,
        )

        max_fee = await self._get_max_fee(
            transaction=deploy_account_tx, max_fee=max_fee, auto_estimate=auto_estimate
        )
        _add_max_fee_to_transaction(deploy_account_tx, max_fee)
        signature = self.signer.sign_transaction(deploy_account_tx)
        return _add_signature_to_transaction(deploy_account_tx, signature)

    async def execute(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> SentTransactionResponse:
        """
        Takes calls and executes transaction

        :param calls: Single call or list of calls
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: SentTransactionResponse
        """
        execute_transaction = await self.sign_invoke_transaction(
            calls, max_fee=max_fee, auto_estimate=auto_estimate
        )
        return await self._client.send_transaction(execute_transaction)

    def sign_message(self, typed_data: TypedData) -> List[int]:
        """
        Sign an TypedData TypedDict for off-chain usage with the starknet private key and return the signature
        This adds a message prefix, so it can't be interchanged with transactions

        :param typed_data: TypedData TypedDict to be signed
        :return: The signature of the TypedData TypedDict
        """
        return self.signer.sign_message(typed_data, self.address)

    async def verify_message(self, typed_data: TypedData, signature: List[int]) -> bool:
        """
        Verify a signature of a TypedData TypedDict

        :param typed_data: TypedData TypedDict to be verified
        :param signature: signature of the TypedData TypedDict
        :return: true if the signature is valid, false otherwise
        """
        typed_data_dataclass = TypedDataDataclass.from_dict(typed_data)
        message_hash = typed_data_dataclass.message_hash(account_address=self.address)
        return await self._verify_message_hash(message_hash, signature)


SignableTransaction = TypeVar(
    "SignableTransaction", InvokeFunction, Declare, DeployAccount
)


def _add_signature_to_transaction(
    tx: SignableTransaction, signature: List[int]
) -> SignableTransaction:
    return dataclasses.replace(tx, signature=signature)


def _add_max_fee_to_transaction(
    tx: SignableTransaction, max_fee: int
) -> SignableTransaction:
    return dataclasses.replace(tx, max_fee=max_fee)


def _parse_call(
    _call: Call, _current_data_len: int, _entire_calldata: List
) -> Tuple[Dict, int, List]:
    _data = {
        "to": _call.to_addr,
        "selector": _call.selector,
        "data_offset": _current_data_len,
        "data_len": len(_call.calldata),
    }
    _current_data_len += len(_call.calldata)
    _entire_calldata += _call.calldata

    return _data, _current_data_len, _entire_calldata


def _merge_calls(calls: Iterable[Call]) -> List:
    calldata = []
    current_data_len = 0
    entire_calldata = []
    for call in calls:
        data, current_data_len, entire_calldata = _parse_call(
            call, current_data_len, entire_calldata
        )
        calldata.append(data)

    return [calldata, entire_calldata]
