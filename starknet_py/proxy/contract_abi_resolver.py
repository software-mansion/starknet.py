import warnings
from enum import Enum
from typing import List, TypedDict, Tuple

from starknet_py.constants import RPC_CLASS_HASH_NOT_FOUND_ERROR
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ContractNotFoundError, ClientError
from starknet_py.net.client_models import Abi, DeclaredContract
from starknet_py.net.models import Address
from starknet_py.proxy.proxy_check import (
    OpenZeppelinProxyCheck,
    ArgentProxyCheck,
    ProxyCheck,
)


class ProxyConfig(TypedDict, total=False):
    """
    Proxy resolving configuration
    """

    proxy_checks: List[ProxyCheck]
    """
    List of classes implementing :class:`starknet_py.proxy.proxy_check.ProxyCheck` ABC,
    that will be used for checking if contract at the address is a proxy contract.
    """


def prepare_proxy_config(proxy_config: ProxyConfig) -> ProxyConfig:
    if "max_steps" in proxy_config:
        warnings.warn(
            "ProxyConfig.max_steps is deprecated. Contract.from_address always makes at most 1 step.",
            category=DeprecationWarning,
        )
    if "proxy_checks" in proxy_config:
        return proxy_config

    proxy_checks = [OpenZeppelinProxyCheck(), ArgentProxyCheck()]
    return {"proxy_checks": proxy_checks}


class ImplementationType(Enum):
    """
    Enum representing transaction types
    """

    CLASS_HASH = "class_hash"
    ADDRESS = "address"


class ContractAbiResolver:
    """
    Class for resolving abi of a contract
    """

    def __init__(
        self,
        address: Address,
        client: Client,
        proxy_config: ProxyConfig,
    ):
        """
        :param address: Contract's address
        :param client: Client used for resolving abi
        :param proxy_config: Proxy config for resolving proxy
        """
        self.address = address
        self.client = client
        self.proxy_config = proxy_config

    async def resolve(self) -> Abi:
        """
        Returns abi of either direct contract or contract proxied by direct contract depending on proxy_config.
        :raises ContractNotFoundError: when contract could not be found at address
        :raises ProxyResolutionError: when given ProxyChecks were not sufficient to resolve proxy
        :raises AbiNotFoundError: when abi is not present in contract class at address
        """
        if len(self.proxy_config) == 0:
            return await self.get_abi_for_address()
        return await self.resolve_abi()

    async def get_abi_for_address(self) -> Abi:
        """
        Returns abi of a contract directly from address.
        :raises ContractNotFoundError: when contract could not be found at address
        :raises AbiNotFoundError: when abi is not present in contract class at address
        """
        contract_class = await self._get_class_by_address(address=self.address)
        if contract_class.abi is None:
            raise AbiNotFoundError()
        return contract_class.abi

    async def resolve_abi(self) -> Abi:
        """
        Returns abi of a contract that is being proxied by contract at address.
        :raises ContractNotFoundError: when contract could not be found at address
        :raises ProxyResolutionError: when given ProxyChecks were not sufficient to resolve proxy
        :raises AbiNotFoundError: when abi is not present in proxied contract class at address
        """
        impl = await self._get_implementation_from_proxy()
        implementation, implementation_type = impl

        if implementation_type == ImplementationType.CLASS_HASH:
            contract_class = await self.client.get_class_by_hash(implementation)
        else:
            contract_class = await self._get_class_by_address(address=implementation)

        if contract_class.abi is None:
            raise AbiNotFoundError()
        return contract_class.abi

    async def _get_implementation_from_proxy(self) -> Tuple[int, ImplementationType]:
        proxy_checks = self.proxy_config.get("proxy_checks", [])
        for proxy_check in proxy_checks:
            implementation = await proxy_check.implementation_hash(
                address=self.address, client=self.client
            )
            if implementation is not None:
                return implementation, ImplementationType.CLASS_HASH

            implementation = await proxy_check.implementation_address(
                address=self.address, client=self.client
            )
            if implementation is not None:
                return implementation, ImplementationType.ADDRESS

        raise ProxyResolutionError()

    async def _get_class_by_address(self, address: Address) -> DeclaredContract:
        try:
            contract_class_hash = await self.client.get_class_hash_at(
                contract_address=address
            )
            contract_class = await self.client.get_class_by_hash(
                class_hash=contract_class_hash
            )
        except ClientError as err:
            if (
                "is not deployed" in err.message
                or err.code == RPC_CLASS_HASH_NOT_FOUND_ERROR
            ):
                raise ContractNotFoundError(address=address) from err
            raise err

        return contract_class


class AbiNotFoundError(Exception):
    """
    Error while resolving contract abi.
    """


class ProxyResolutionError(Exception):
    """
    Error while resolving proxy using ProxyChecks.
    """

    def __init__(self):
        self.message = "Couldn't resolve proxy using given ProxyChecks"
        super().__init__(self.message)
