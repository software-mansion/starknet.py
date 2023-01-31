import re
import warnings
from enum import Enum
from typing import AsyncGenerator, List, Tuple, TypedDict

from starknet_py.abi.shape import AbiDictList
from starknet_py.constants import (
    RPC_CLASS_HASH_NOT_FOUND_ERROR,
    RPC_CONTRACT_NOT_FOUND_ERROR,
    RPC_INVALID_MESSAGE_SELECTOR_ERROR,
)
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ClientError, ContractNotFoundError
from starknet_py.net.client_models import DeclaredContract
from starknet_py.net.models import Address
from starknet_py.proxy.proxy_check import (
    ArgentProxyCheck,
    OpenZeppelinProxyCheck,
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

    async def resolve(self) -> AbiDictList:
        """
        Returns abi of either direct contract or contract proxied by direct contract depending on proxy_config.
        :raises ContractNotFoundError: when contract could not be found at address
        :raises ProxyResolutionError: when given ProxyChecks were not sufficient to resolve proxy
        :raises AbiNotFoundError: when abi is not present in contract class at address
        """
        if len(self.proxy_config) == 0:
            return await self.get_abi_for_address()
        return await self.resolve_abi()

    async def get_abi_for_address(self) -> AbiDictList:
        """
        Returns abi of a contract directly from address.
        :raises ContractNotFoundError: when contract could not be found at address
        :raises AbiNotFoundError: when abi is not present in contract class at address
        """
        contract_class = await _get_class_at(address=self.address, client=self.client)
        if contract_class.abi is None:
            raise AbiNotFoundError()
        return contract_class.abi

    async def resolve_abi(self) -> AbiDictList:
        """
        Returns abi of a contract that is being proxied by contract at address.
        :raises ContractNotFoundError: when contract could not be found at address
        :raises ProxyResolutionError: when given ProxyChecks were not sufficient to resolve proxy
        :raises AbiNotFoundError: when abi is not present in proxied contract class at address
        """
        implementation_generator = self._get_implementation_from_proxy()

        # implementation is either a class_hash or address
        async for implementation, implementation_type in implementation_generator:
            try:
                if implementation_type == ImplementationType.CLASS_HASH:
                    contract_class = await self.client.get_class_by_hash(implementation)
                else:
                    contract_class = await _get_class_at(
                        address=implementation, client=self.client
                    )

                if contract_class.abi is None:
                    # Some contract_class has been found, but it does not have abi
                    raise AbiNotFoundError()
                return contract_class.abi
            except ClientError as err:
                if not (
                    "is not declared" in err.message
                    or err.code == RPC_CLASS_HASH_NOT_FOUND_ERROR
                    or isinstance(err, ContractNotFoundError)
                ):
                    raise err

        raise ProxyResolutionError()

    async def _get_implementation_from_proxy(
        self,
    ) -> AsyncGenerator[Tuple[int, ImplementationType], None]:
        proxy_checks = self.proxy_config.get("proxy_checks", [])
        for proxy_check in proxy_checks:
            try:
                implementation = await proxy_check.implementation_hash(
                    address=self.address, client=self.client
                )
                if implementation is not None:
                    yield implementation, ImplementationType.CLASS_HASH

                implementation = await proxy_check.implementation_address(
                    address=self.address, client=self.client
                )
                if implementation is not None:
                    yield implementation, ImplementationType.ADDRESS
            except ClientError as err:
                err_msg = r"(Entry point 0x[0-9a-f]+ not found in contract)|(is not declared)|(is not deployed)"
                if not (
                    re.search(err_msg, err.message, re.IGNORECASE)
                    or err.code
                    in [
                        RPC_INVALID_MESSAGE_SELECTOR_ERROR,
                        RPC_CLASS_HASH_NOT_FOUND_ERROR,
                        RPC_CONTRACT_NOT_FOUND_ERROR,
                    ]
                ):
                    raise err


class AbiNotFoundError(Exception):
    """
    Error while resolving contract abi.
    """


class ProxyResolutionError(Exception):
    """
    Error while resolving proxy using ProxyChecks.
    """

    def __init__(self):
        self.message = "Couldn't resolve proxy using given ProxyChecks."
        super().__init__(self.message)


async def _get_class_at(address: Address, client: Client) -> DeclaredContract:
    try:
        contract_class_hash = await client.get_class_hash_at(contract_address=address)
        contract_class = await client.get_class_by_hash(class_hash=contract_class_hash)
    except ClientError as err:
        if (
            "is not deployed" in err.message
            or err.code == RPC_CLASS_HASH_NOT_FOUND_ERROR
        ):
            raise ContractNotFoundError(address=address) from err
        raise err

    return contract_class
