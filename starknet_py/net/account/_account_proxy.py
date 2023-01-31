__all__ = []

import dataclasses
from typing import List, Optional, Union

from starknet_py.constants import QUERY_VERSION_BASE
from starknet_py.net import AccountClient
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    Calls,
    Declare,
    DeployAccount,
    Invoke,
    SentTransactionResponse,
)
from starknet_py.net.models import AddressRepresentation
from starknet_py.net.models.typed_data import TypedData


class AccountProxy(BaseAccount):
    def __init__(self, account_client: AccountClient):
        self._account_client = account_client

    @property
    def address(self) -> int:
        return self._account_client.address

    @property
    def client(self) -> Client:
        return self._account_client.client

    @property
    def supported_transaction_version(self) -> int:
        return self._account_client.supported_tx_version

    async def get_nonce(self) -> int:
        # pylint: disable=protected-access
        return await self._account_client._get_nonce()

    async def get_balance(
        self, token_address: Optional[AddressRepresentation] = None
    ) -> int:
        return await self._account_client.get_balance(token_address=token_address)

    async def sign_for_fee_estimate(
        self, transaction: Union[Invoke, Declare, DeployAccount]
    ) -> Union[Invoke, Declare, DeployAccount]:
        version = self.supported_transaction_version + QUERY_VERSION_BASE
        transaction = dataclasses.replace(transaction, version=version)

        signature = self._account_client.signer.sign_transaction(transaction)
        transaction = dataclasses.replace(transaction, signature=signature)

        return transaction

    async def sign_invoke_transaction(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Invoke:
        return await self._account_client.sign_invoke_transaction(
            calls=calls, max_fee=max_fee, auto_estimate=auto_estimate
        )

    async def sign_declare_transaction(
        self,
        compiled_contract: str,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Declare:
        return await self._account_client.sign_declare_transaction(
            compiled_contract=compiled_contract,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
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
    ) -> SentTransactionResponse:
        return await self._account_client.execute(
            calls=calls, max_fee=max_fee, auto_estimate=auto_estimate
        )

    def sign_message(self, typed_data: TypedData) -> List[int]:
        return self._account_client.sign_message(typed_data=typed_data)

    async def verify_message(self, typed_data: TypedData, signature: List[int]) -> bool:
        return await self._account_client.verify_message(
            typed_data=typed_data, signature=signature
        )
