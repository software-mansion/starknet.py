# Needed because of string typed Contract
# pyright: reportUndefinedVariable=false

from abc import ABC, abstractmethod

from starknet_py.constants import OZ_PROXY_STORAGE_KEY
from starknet_py.net.models import parse_address


# noinspection PyUnresolvedReferences
class ProxyCheck(ABC):
    @abstractmethod
    async def is_proxy(self, contract: "Contract") -> bool:
        """
        :return: `True` if contract is a proxy or `False` if it is not
        """

    @abstractmethod
    async def implementation_address(self, contract: "Contract") -> int:
        """
        :return: Address of contract being proxied by `contract` given as a parameter
        """


# noinspection PyUnresolvedReferences
class ArgentProxyCheck(ProxyCheck):
    async def is_proxy(self, contract: "Contract") -> bool:
        return "get_implementation" in contract.functions

    async def implementation_address(self, contract: "Contract") -> int:
        res = await contract.functions["get_implementation"].call()
        return res[0]


# noinspection PyUnresolvedReferences
class OpenZeppelinProxyCheck(ProxyCheck):
    def __init__(self):
        self.storage_key = OZ_PROXY_STORAGE_KEY
        self.cache = {}

    async def is_proxy(self, contract: "Contract") -> bool:
        return await self.implementation_address(contract) != 0

    async def implementation_address(self, contract: "Contract") -> int:
        if contract.address not in self.cache:
            res = await contract.client.get_storage_at(
                contract_address=contract.address,
                key=self.storage_key,
                block_hash="latest",
            )
            self.cache[contract.address] = parse_address(res)
        return self.cache[contract.address]
