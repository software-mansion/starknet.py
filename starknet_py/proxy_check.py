from abc import ABC, abstractmethod

from starkware.starknet.public.abi import get_storage_var_address

from starknet_py.net.models import parse_address


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


class ArgentProxyCheck(ProxyCheck):
    async def is_proxy(self, contract: "Contract") -> bool:
        return "get_implementation" in contract.functions

    async def implementation_address(self, contract: "Contract") -> int:
        res = await contract.functions["get_implementation"].call()
        return res[0]


class OpenZeppelinProxyCheck(ProxyCheck):
    def __init__(self):
        self.storage_key = generate_oz_storage_key()

    async def is_proxy(self, contract: "Contract") -> bool:
        return await self.implementation_address(contract) != 0

    async def implementation_address(self, contract: "Contract") -> int:
        res = await contract.client.get_storage_at(
            contract_address=contract.address, key=self.storage_key
        )
        return parse_address(res)


def generate_oz_storage_key():
    return get_storage_var_address("Proxy_implementation_address")
