# Needed because of string typed Contract
# pyright: reportUndefinedVariable=false

from abc import ABC, abstractmethod
from starkware.starknet.public.abi import get_storage_var_address

# noinspection PyUnresolvedReferences
class ProxyCheck(ABC):
    @abstractmethod
    async def is_proxy(self, contract: "Contract") -> bool:
        """
        :return: `True` if contract is a proxy or `False` if it is not
        """

    @abstractmethod
    async def implementation(self, contract: "Contract") -> int:
        """
        :return: Implementation (either class hash or contract address)
            of contract being proxied by `contract` given as a parameter
            or 0 if implementation does not exist
        """


# noinspection PyUnresolvedReferences
class ArgentProxyCheck(ProxyCheck):
    async def is_proxy(self, contract: "Contract") -> bool:
        return "get_implementation" in contract.functions

    async def implementation(self, contract: "Contract") -> int:
        try:
            (result,) = await contract.functions["get_implementation"].call()
            return result
        except KeyError:
            return 0


# noinspection PyUnresolvedReferences
class OpenZeppelinProxyCheck(ProxyCheck):
    async def is_proxy(self, contract: "Contract") -> bool:
        return await self.implementation(contract) != 0

    async def implementation(self, contract: "Contract") -> int:
        proxy_implementation_hash = await contract.client.get_storage_at(
            contract_address=contract.address,
            key=get_storage_var_address("Proxy_implementation_hash"),
            block_hash="latest",
        )
        if proxy_implementation_hash != 0:
            return proxy_implementation_hash

        proxy_implementation_address = await contract.client.get_storage_at(
            contract_address=contract.address,
            key=get_storage_var_address("Proxy_implementation_address"),
            block_hash="latest",
        )
        return proxy_implementation_address
