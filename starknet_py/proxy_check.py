# Needed because of string typed Contract
# pyright: reportUndefinedVariable=false

from abc import ABC, abstractmethod
from typing import List

from starkware.starknet.public.abi import get_storage_var_address

# noinspection PyUnresolvedReferences
class ProxyCheck(ABC):
    @abstractmethod
    async def implementation(self, contract: "Contract") -> int:
        """
        :return: Implementation (either class hash or contract address)
            of contract being proxied by `contract` given as a parameter
            or 0 if implementation does not exist
        """


# noinspection PyUnresolvedReferences
class ArgentProxyCheck(ProxyCheck):
    async def implementation(self, contract: "Contract") -> int:
        try:
            (result,) = await contract.functions["get_implementation"].call()
            return result
        except KeyError:
            return 0


# noinspection PyUnresolvedReferences
class OpenZeppelinProxyCheck(ProxyCheck):
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
