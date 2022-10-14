# Needed because of string typed Contract
# pyright: reportUndefinedVariable=false
import warnings
from enum import Enum
from typing import Union, List, TypedDict, Tuple

from starknet_py.net.client import Client
from starknet_py.net.client_errors import ContractNotFoundError, ClientError
from starknet_py.net.client_models import Abi, DeclaredContract
from starknet_py.net.models import Address
from starknet_py.proxy_check import (
    ProxyResolutionError,
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
    List of classes implementing :class:`starknet_py.proxy_check.ProxyCheck` ABC,
    that will be used for checking if contract at the address is a proxy contract.
    """


def prepare_proxy_config(proxy_config: Union[bool, ProxyConfig]) -> ProxyConfig:
    if isinstance(proxy_config, bool):
        if not proxy_config:
            return ProxyConfig()
        proxy_config = ProxyConfig()

    if "max_steps" in proxy_config:
        warnings.warn(
            "ProxyConfig.max_steps is deprecated. Contract.from_address always makes at most 1 step.",
            category=DeprecationWarning,
        )
    proxy_checks = [OpenZeppelinProxyCheck(), ArgentProxyCheck()]
    return {"proxy_checks": proxy_checks, **proxy_config}


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

    @staticmethod
    async def resolve_direct(
        address: Address,
        client: Client,
    ) -> Abi:
        """
        Returns abi of a contract directly from given address.
        """
        contract_class = await ContractAbiResolver._get_class_by_address(
            address=address, client=client
        )
        return contract_class.abi or []

    @staticmethod
    async def resolve_proxy_step(
        proxy_contract: "Contract",
        proxy_config: ProxyConfig,
    ) -> Abi:
        """
        Returns abi of a contract that is being proxied by proxy_contract.
        """
        impl = await ContractAbiResolver._get_implementation_from_proxy(
            proxy_contract=proxy_contract, proxy_config=proxy_config
        )
        implementation, implementation_type = impl
        proxy_client = proxy_contract.client

        if implementation_type == ImplementationType.CLASS_HASH:
            contract_class = await proxy_client.get_class_by_hash(implementation)
        elif implementation_type == ImplementationType.ADDRESS:
            contract_class = await ContractAbiResolver._get_class_by_address(
                address=implementation, client=proxy_client
            )
        else:
            return []

        return contract_class.abi or []

    @staticmethod
    async def _get_implementation_from_proxy(
        proxy_contract: "Contract", proxy_config: ProxyConfig
    ) -> Tuple[int, ImplementationType]:
        implementation, proxy_checks = None, proxy_config.get("proxy_checks", [])
        for proxy_check in proxy_checks:
            implementation = await proxy_check.implementation_hash(proxy_contract)
            if implementation is not None:
                return implementation, ImplementationType.CLASS_HASH

            implementation = await proxy_check.implementation_address(proxy_contract)
            if implementation is not None:
                return implementation, ImplementationType.ADDRESS

        raise ProxyResolutionError(proxy_checks)

    @staticmethod
    async def _get_class_by_address(
        address: Address, client: Client
    ) -> DeclaredContract:
        contract_class_hash = 0
        try:
            contract_class_hash = await client.get_class_hash_at(
                contract_address=address
            )
            contract_class = await client.get_class_by_hash(
                class_hash=contract_class_hash
            )
        except ClientError as err:
            if "is not deployed" in err.message:
                raise ContractNotFoundError(block_hash="latest") from err
            raise err

        return contract_class
