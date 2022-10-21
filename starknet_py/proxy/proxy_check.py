import re
from abc import ABC, abstractmethod
from typing import Optional

from starkware.starknet.public.abi import (
    get_storage_var_address,
    get_selector_from_name,
)

from starknet_py.net.client import Client
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call
from starknet_py.net.models import Address


class ProxyCheck(ABC):
    @abstractmethod
    async def implementation_address(
        self, address: Address, client: Client
    ) -> Optional[int]:
        """
        :return: Implementation address of contract being proxied by proxy contract at `address`
            given as a parameter or None if implementation does not exist.
        """

    @abstractmethod
    async def implementation_hash(
        self, address: Address, client: Client
    ) -> Optional[int]:
        """
        :return: Implementation class hash of contract being proxied by proxy contract at `address`
            given as a parameter or None if implementation does not exist.
        """


class ArgentProxyCheck(ProxyCheck):
    async def implementation_address(
        self, address: Address, client: Client
    ) -> Optional[int]:
        call = self._get_implementation_call(address=address)
        try:
            (implementation_address,) = await client.call_contract(invoke_tx=call)
            await client.get_class_hash_at(contract_address=implementation_address)
        except ClientError as err:
            if re.search(
                r"(Entry point 0x[0-9a-f]+ not found in contract)|(is not declared)",
                err.message,
                re.I,
            ):
                return None
            raise err
        return implementation_address

    async def implementation_hash(
        self, address: Address, client: Client
    ) -> Optional[int]:
        call = ArgentProxyCheck._get_implementation_call(address=address)
        try:
            (implementation_hash,) = await client.call_contract(invoke_tx=call)
            await client.get_class_by_hash(class_hash=implementation_hash)
        except ClientError as err:
            if re.search(
                r"(Entry point 0x[0-9a-f]+ not found in contract)|(is not deployed)",
                err.message,
                re.I,
            ):
                return None
            raise err
        return implementation_hash

    @staticmethod
    def _get_implementation_call(address: Address) -> Call:
        return Call(
            to_addr=address,
            selector=get_selector_from_name("get_implementation"),
            calldata=[],
        )


class OpenZeppelinProxyCheck(ProxyCheck):
    async def implementation_address(
        self, address: Address, client: Client
    ) -> Optional[int]:
        return await self._get_storage_at(
            address=address, client=client, key="Proxy_implementation_address"
        )

    async def implementation_hash(
        self, address: Address, client: Client
    ) -> Optional[int]:
        return await self._get_storage_at(
            address=address, client=client, key="Proxy_implementation_hash"
        )

    @staticmethod
    async def _get_storage_at(
        address: Address, client: Client, key: str
    ) -> Optional[int]:
        result = await client.get_storage_at(
            contract_address=address,
            key=get_storage_var_address(key),
            block_hash="latest",
        )
        return result or None
