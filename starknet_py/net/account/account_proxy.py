from typing import List, Optional, Union

from starknet_py.net import AccountClient
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    Calls,
    SentTransactionResponse,
    Declare,
    InvokeFunction,
    EstimatedFee,
    Hash,
    Tag,
)
from starknet_py.net.models import AddressRepresentation
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.models.typed_data import TypedData


class _AccountProxy(BaseAccount):
    def __init__(self, account_client: AccountClient):
        self._account_client = account_client

    @property
    def client(self) -> Client:
        return self._account_client.client

    @property
    def supported_tx_version(self) -> int:
        return self._account_client.supported_tx_version

    async def signed_estimate_fee(
        self,
        tx: Union[InvokeFunction, Declare, DeployAccount],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> EstimatedFee:
        return await self._account_client.estimate_fee(
            tx=tx, block_hash=block_hash, block_number=block_number
        )

    async def get_nonce(self) -> int:
        return await self._account_client._get_nonce()

    async def get_balance(
        self, token_address: Optional[AddressRepresentation] = None
    ) -> int:
        return await self._account_client.get_balance(token_address=token_address)

    async def sign_invoke_transaction(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        **kwargs,
    ) -> InvokeFunction:
        return await self._account_client.sign_invoke_transaction(
            calls=calls, max_fee=max_fee, auto_estimate=auto_estimate, **kwargs
        )

    async def sign_declare_transaction(
        self,
        compiled_contract: str,
        *,
        cairo_path: Optional[List[str]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        **kwargs,
    ) -> Declare:
        return await self._account_client.sign_declare_transaction(
            compiled_contract=compiled_contract,
            cairo_path=cairo_path,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
            **kwargs,
        )

    async def sign_deploy_account_transaction(
        self,
        class_hash: int,
        contract_address_salt: int,
        constructor_calldata: Optional[List[int]] = None,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeployAccount:
        return await self._account_client.sign_deploy_account_transaction(
            class_hash=class_hash,
            contract_address_salt=contract_address_salt,
            constructor_calldata=constructor_calldata,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
        )

    async def execute(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        **kwargs,
    ) -> SentTransactionResponse:
        return await self._account_client.execute(
            calls=calls, max_fee=max_fee, auto_estimate=auto_estimate, **kwargs
        )

    def sign_message(self, typed_data: TypedData) -> List[int]:
        return self._account_client.sign_message(typed_data=typed_data)

    def hash_message(self, typed_data: TypedData) -> int:
        return self._account_client.hash_message(typed_data=typed_data)

    async def verify_message(self, typed_data: TypedData, signature: List[int]) -> bool:
        return await self._account_client.verify_message(
            typed_data=typed_data, signature=signature
        )

    @staticmethod
    def account_or_proxy(account: Union[AccountClient, BaseAccount]) -> BaseAccount:
        if isinstance(account, BaseAccount):
            return account
        if isinstance(account, AccountClient):
            return _AccountProxy(account)
        raise ValueError("Incompatible account passed to account_or_proxy")
