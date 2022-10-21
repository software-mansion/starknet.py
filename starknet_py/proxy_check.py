from abc import ABC, abstractmethod
from typing import List, Optional

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
        call = Call(
            to_addr=address,
            selector=get_selector_from_name("get_implementation"),
            calldata=[],
        )
        try:
            (implementation_address,) = await client.call_contract(invoke_tx=call)
            await client.get_class_hash_at(contract_address=implementation_address)
        except ClientError:
            return None
        return implementation_address

    async def implementation_hash(
        self, address: Address, client: Client
    ) -> Optional[int]:
        call = Call(
            to_addr=address,
            selector=get_selector_from_name("get_implementation"),
            calldata=[],
        )
        try:
            (implementation_hash,) = await client.call_contract(invoke_tx=call)
            await client.get_class_by_hash(class_hash=implementation_hash)
        except ClientError:
            return None
        return implementation_hash


class OpenZeppelinProxyCheck(ProxyCheck):
    async def implementation_address(
        self, address: Address, client: Client
    ) -> Optional[int]:
        proxy_implementation_address = await client.get_storage_at(
            contract_address=address,
            key=get_storage_var_address("Proxy_implementation_address"),
            block_hash="latest",
        )
        return proxy_implementation_address or None

    async def implementation_hash(
        self, address: Address, client: Client
    ) -> Optional[int]:
        proxy_implementation_hash = await client.get_storage_at(
            contract_address=address,
            key=get_storage_var_address("Proxy_implementation_hash"),
            block_hash="latest",
        )
        return proxy_implementation_hash or None


class ProxyResolutionError(Exception):
    """
    Error while resolving proxy using ProxyChecks.
    """

    def __init__(self, proxy_checks: List[ProxyCheck]):
        proxy_checks_classes = [proxy_check.__class__ for proxy_check in proxy_checks]
        self.message = (
            f"Couldn't resolve proxy using given ProxyChecks ({proxy_checks_classes})"
        )
        super().__init__(self.message)
