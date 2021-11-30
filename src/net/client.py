import asyncio
from typing import Optional, List, Dict

from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    FeederGatewayClient,
    CastableToHash,
    JsonObject,
)
from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from services.external_api.base_client import RetryConfig
from starkware.starknet.services.api.gateway.transaction import (
    InvokeFunction,
    Transaction,
)

from src.constants import TxStatus

dns = "alpha4.starknet.io"


class Client:
    def __init__(self, retry_config: Optional[RetryConfig] = None):
        retry_config = retry_config or RetryConfig(1)
        feeder_gateway_url = f"https://{dns}/feeder_gateway"
        self._feeder_gateway = FeederGatewayClient(
            url=feeder_gateway_url, retry_config=retry_config
        )

        gateway_url = f"https://{dns}/gateway"
        self._gateway = GatewayClient(url=gateway_url, retry_config=retry_config)

    # View methods
    async def get_contract_addresses(self) -> Dict[str, str]:
        return await self._feeder_gateway.get_contract_addresses()

    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[int] = None,
    ) -> Dict[str, List[str]]:
        return await self._feeder_gateway.call_contract(
            invoke_tx,
            block_hash,
            block_number,
        )

    async def get_block(
        self,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[int] = None,
    ) -> JsonObject:
        return await self._feeder_gateway.get_block(block_hash, block_number)

    async def get_code(
        self,
        contract_address: int,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[int] = None,
    ) -> List[str]:
        return await self._feeder_gateway.get_code(
            contract_address,
            block_hash,
            block_number,
        )

    async def get_storage_at(
        self,
        contract_address: int,
        key: int,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[int] = None,
    ) -> str:
        return await self._feeder_gateway.get_storage_at(
            contract_address,
            key,
            block_hash,
            block_number,
        )

    async def get_transaction_status(
        self, tx_hash: Optional[CastableToHash], tx_id: Optional[int] = None
    ) -> JsonObject:
        return await self._feeder_gateway.get_transaction_status(
            tx_hash,
            tx_id,
        )

    async def get_transaction(
        self, tx_hash: Optional[CastableToHash], tx_id: Optional[int] = None
    ) -> JsonObject:
        return await self._feeder_gateway.get_transaction(
            tx_hash,
            tx_id,
        )

    async def get_transaction_receipt(
        self, tx_hash: Optional[CastableToHash], tx_id: Optional[int] = None
    ) -> JsonObject:
        return await self._feeder_gateway.get_transaction_receipt(
            tx_hash,
            tx_id,
        )

    async def wait_for_tx(
        self,
        tx_hash: Optional[CastableToHash],
        wait_for_accept: Optional[bool] = False,
        check_interval=5,
    ) -> (int, TxStatus):
        """

        :param tx_hash: Transaction's hash
        :param wait_for_accept: If true waits for ACCEPTED_ONCHAIN status, otherwise waits for at least PENDING
        :param check_interval: Defines interval between checks
        :return: number of block, tx status
        """
        if check_interval <= 0:
            raise ValueError("check_interval has to bigger than 0.")

        first_run = True
        while True:
            result = await self.get_transaction(tx_hash=tx_hash)
            status = TxStatus[result["status"]]

            if status == TxStatus.ACCEPTED_ONCHAIN:
                return result["block_number"], status
            elif status == TxStatus.PENDING:
                if not wait_for_accept and "block_number" in result:
                    return result["block_number"], status
            elif status == TxStatus.REJECTED:
                raise Exception(f"Transaction [{tx_hash}] was rejected.")
            elif status == TxStatus.NOT_RECEIVED:
                if not first_run:
                    raise Exception(f"Transaction [{tx_hash}] was not received.")
            elif status != TxStatus.RECEIVED:
                raise Exception(f"Unknown status [{status}]")

            first_run = False
            await asyncio.sleep(check_interval)

    # Mutating methods
    async def add_transaction(
        self, tx: Transaction, token: Optional[str] = None
    ) -> Dict[str, int]:
        return await self._gateway.add_transaction(tx, token)
