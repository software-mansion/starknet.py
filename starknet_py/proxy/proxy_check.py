import re
from abc import ABC, abstractmethod
from typing import Optional, Callable

from starkware.starknet.public.abi import (
    get_storage_var_address,
    get_selector_from_name,
)

from starknet_py.constants import RPC_INVALID_MESSAGE_SELECTOR_ERROR
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
        return await self.get_implementation(
            address=address,
            client=client,
            get_class_func=client.get_class_hash_at,
            regex_err_msg=r"(is not deployed)",
        )

    async def implementation_hash(
        self, address: Address, client: Client
    ) -> Optional[int]:
        return await self.get_implementation(
            address=address,
            client=client,
            get_class_func=client.get_class_by_hash,
            regex_err_msg=r"(is not declared)",
        )

    @staticmethod
    async def get_implementation(
        address: Address, client: Client, get_class_func: Callable, regex_err_msg: str
    ) -> Optional[int]:
        call = ArgentProxyCheck._get_implementation_call(address=address)
        err_msg = r"(Entry point 0x[0-9a-f]+ not found in contract)|" + regex_err_msg
        try:
            (implementation,) = await client.call_contract(call=call)
            await get_class_func(implementation)
        except ClientError as err:
            if (
                re.search(err_msg, err.message, re.IGNORECASE)
                or err.code == RPC_INVALID_MESSAGE_SELECTOR_ERROR
            ):
                return None
            raise err
        return implementation

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
        return await self._get_storage_at_or_none(
            address=address, client=client, key="Proxy_implementation_address"
        )

    async def implementation_hash(
        self, address: Address, client: Client
    ) -> Optional[int]:
        return await self._get_storage_at_or_none(
            address=address, client=client, key="Proxy_implementation_hash"
        )

    @staticmethod
    async def _get_storage_at_or_none(
        address: Address, client: Client, key: str
    ) -> Optional[int]:
        result = await client.get_storage_at(
            contract_address=address,
            key=get_storage_var_address(key),
            block_hash="latest",
        )
        return result or None
