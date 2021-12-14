import asyncio
from typing import Optional, List, Dict

from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    FeederGatewayClient,
    CastableToHash,
    JsonObject,
)
from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from services.external_api.base_client import RetryConfig

from starknet.constants import TxStatus
from starknet.utils.sync import add_sync_methods
from starknet.utils.types import net_address_from_net, InvokeFunction, Transaction


@add_sync_methods
class Client:
    def __init__(self, net: str, n_retries: Optional[int] = 1):
        """

        :param net: Target network for the client. Can be a string with URL or one of ``"mainnet"``, ``"testnet"``
        :param n_retries: Number of retries client will attempt before failing a request
        """
        host = net_address_from_net(net)
        retry_config = RetryConfig(n_retries)
        feeder_gateway_url = f"{host}/feeder_gateway"
        self._feeder_gateway = FeederGatewayClient(
            url=feeder_gateway_url, retry_config=retry_config
        )

        gateway_url = f"{host}/gateway"
        self._gateway = GatewayClient(url=gateway_url, retry_config=retry_config)

    # View methods
    async def get_contract_addresses(self) -> Dict[str, str]:
        """
        :return: Dictionary containing all of the contract's addresses
        """
        return await self._feeder_gateway.get_contract_addresses()

    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        """
        Calls the contract with given instance of InvokeTransaction

        :param invoke_tx: The invoke transaction
        :param block_hash: Block hash to execute the contract at specific point of time
        :param block_number: Block number to execute the contract at
        :return: List of integers representing contract's function output (structured like calldata)
        """
        response = await self._feeder_gateway.call_contract(
            invoke_tx,
            block_hash,
            block_number,
        )
        return [int(v, 16) for v in response["result"]]

    async def get_block(
        self,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[int] = None,
    ) -> JsonObject:
        """
        Retrieve the block's data by its number or hash

        :param block_hash: Block's hash
        :param block_number: Block's number
        :return: Dictionary with block's transactions
        """
        return await self._feeder_gateway.get_block(block_hash, block_number)

    async def get_code(
        self,
        contract_address: int,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[int] = None,
    ) -> List[str]:
        """

        :param contract_address: Address of the contract on Starknet
        :param block_hash: Get code at specific block hash
        :param block_number: Get code at given block number
        :return: JSON representation of compiled code of the contract, with ABI alongside
        """
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
        """
        :param contract_address: Contract's address on Starknet
        :param key: An address of the storage variable inside of the contract.
                    Can be retrieved using ``starkware.starknet.public.abi.get_storage_var_address(<name>)``
        :param block_hash: Fetches the value of the variable at given block hash
        :param block_number: See above, uses block number instead of hash
        :return: Storage value of given contract
        """
        return await self._feeder_gateway.get_storage_at(
            contract_address,
            key,
            block_hash,
            block_number,
        )

    async def get_transaction_status(
        self, tx_hash: Optional[CastableToHash], tx_id: Optional[int] = None
    ) -> JsonObject:
        """
        :param tx_hash: Transaction's hash
        :param tx_id: Transaction's index
        :return: Dictionary containing tx's status
        """
        return await self._feeder_gateway.get_transaction_status(
            tx_hash,
            tx_id,
        )

    async def get_transaction(
        self, tx_hash: Optional[CastableToHash], tx_id: Optional[int] = None
    ) -> JsonObject:
        """
        :param tx_hash: Transaction's hash
        :param tx_id: Transaction's index
        :return: Dictionary representing JSON of the transaction on Starknet
        """
        return await self._feeder_gateway.get_transaction(
            tx_hash,
            tx_id,
        )

    async def get_transaction_receipt(
        self, tx_hash: Optional[CastableToHash], tx_id: Optional[int] = None
    ) -> JsonObject:
        """
        :param tx_hash: Transaction's hash
        :param tx_id: Transaction's index
        :return: Dictionary representing JSON of the transaction's receipt on Starknet
        """
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
        Awaits for transaction to get accepted or at least pending by polling its status

        :param tx_hash: Transaction's hash
        :param wait_for_accept: If true waits for ACCEPTED_ONCHAIN status, otherwise waits for at least PENDING
        :param check_interval: Defines interval between checks
        :return: tuple(block number, ``starknet.constants.TxStatus``)
        """
        if check_interval <= 0:
            raise ValueError("check_interval has to bigger than 0.")

        first_run = True
        while True:
            result = await self.get_transaction(tx_hash=tx_hash)
            status = TxStatus[result["status"]]

            if status in (TxStatus.ACCEPTED_ONCHAIN, TxStatus.ACCEPTED_ON_L1):
                return result["block_number"], status
            if status == TxStatus.PENDING:
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
        """
        :param tx: Transaction object (i.e. InvokeFunction, Deploy).
                   A subclass of ``starkware.starknet.services.api.gateway.transaction.Transaction``
        :param token: Optional token for Starknet API access, appended in a query string
        :return: Dictionary with `code`, `transaction_hash`
        """
        return await self._gateway.add_transaction(tx, token)
