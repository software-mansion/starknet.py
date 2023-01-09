from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict

from starkware.starknet.public.abi import (
    get_selector_from_name,
    get_storage_var_address,
)

from starknet_py.constants import (
    DEFAULT_ENTRY_POINT_NAME,
    RPC_CLASS_HASH_NOT_FOUND_ERROR,
    RPC_CONTRACT_NOT_FOUND_ERROR,
)
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ClientError, ContractNotFoundError
from starknet_py.net.client_models import Abi, Call, DeclaredContract
from starknet_py.net.models import Address
from starknet_py.proxy.proxy_check import ProxyCheck


class ProxyConfig(TypedDict, total=False):
    """
    Proxy resolving configuration.

    .. deprecated:: 0.X.0 TODO
        ProxyConfig has been deprecated.
        To resolve custom Proxies, use keyword parameter `get_implementation_func` in :meth:`Contract.from_address`.
    """

    proxy_checks: List[ProxyCheck]
    """
    List of classes implementing :class:`starknet_py.proxy.proxy_check.ProxyCheck` ABC,
    that will be used for checking if contract at the address is a proxy contract.
    """


class ContractAbiResolver:
    """
    Class for resolving ABI of a contract.
    Can resolve ABI of proxied contracts.
    """

    def __init__(
        self,
        address: Address,
        client: Client,
        *,
        get_implementation_func: Optional[Callable] = None,
    ):
        """
        :param address: Contract's address.
        :param client: Client used for resolving abi.
        :param get_implementation_func: Used for resolving Proxy contracts.
            Function returning class_hashes / addresses of the proxied implementation.

            First returned list contains implementations (class_hashes / addresses) from selectors.
            Second returned list contains implementations (class_hashes / addresses) from storage variables.

            See :meth:`ProxyResolver.default_get_implementation_func` for default implementation.
        """
        self.address = address
        self.client = client
        self.get_implementation_func = get_implementation_func

        self.direct_abi = None
        self.proxied_abi = None
        self.direct_contract_class = None

    async def resolve(self) -> Tuple[Abi, Optional[Abi]]:
        """
        Resolves abi of a contract.
        Optionally, if direct contract is a proxy, can resolve abi of the proxied contract.

        :raises AbiNotFoundError: When abi of a contract was not found.
        :return: (abi of direct contract, abi of proxied contract or None).
        """
        self.direct_contract_class = await ContractClassResolver.get_class_at(
            self.address, self.client
        )

        if self.direct_contract_class.abi is None:
            raise AbiNotFoundError()

        self.direct_abi = self.direct_contract_class.abi

        if self.get_implementation_func is not None:
            self.proxied_abi = await self._resolve_proxied_abi()

        return self.direct_abi, self.proxied_abi

    async def _resolve_proxied_abi(self) -> Optional[Abi]:
        assert self.direct_abi is not None
        if not self._is_proxy_contract(self.direct_abi):
            return None

        assert self.get_implementation_func is not None
        (
            selector_implementations,
            storage_var_implementations,
        ) = await self.get_implementation_func(
            self.direct_abi, self.address, self.client
        )

        abi = await self._get_abi_for_contract_class(selector_implementations)
        return abi or await self._get_abi_for_contract_class(
            storage_var_implementations
        )

    async def _get_abi_for_contract_class(
        self, implementations: List[int]
    ) -> Optional[Abi]:
        contract_class = await ContractClassResolver.resolve(
            implementations, self.client
        )
        if contract_class:
            return contract_class.abi

    @staticmethod
    def _is_proxy_contract(abi: Abi) -> bool:
        abi_entry_names = [abi_entry["name"] for abi_entry in abi]
        return DEFAULT_ENTRY_POINT_NAME in abi_entry_names


class ContractAbiResolverException(Exception):
    """
    Base class for all ContractAbiResolver exceptions.
    """


class AbiNotFoundError(ContractAbiResolverException):
    """
    Abi not found at given address.
    """


class ProxyResolver:
    """
    Implements default `get_implementation_func`.
    """

    @staticmethod
    async def default_get_implementation_func(  # pylint: disable=unused-argument
        proxy_abi: Abi,
        proxy_address: Address,
        client: Client,
    ) -> Tuple[List[int], List[int]]:
        """
        Returns implementation class_hashes / addresses of the proxied implementation.
        First returned list contains implementations (class_hashes / addresses) from selectors.
        Second returned list contains implementations (class_hashes / addresses) from storage variables.

        This default `get_implementation_func` uses predefined selectors and storage variables.

        :param proxy_abi: Abi of the proxy contract.
        :param proxy_address: Address of the proxy contract.
        :param client: Client used for getting implementation.
        :return: (selector_implementations, storage_var_implementations).
        """
        kwargs = locals()
        selectors = [
            "get_implementation",
            "implementation",
            "getImplementationHash",
            "get_implementation_hash",
        ]
        storage_vars = [
            "Proxy_implementation_hash",
            "implementation",
            "implementation_hash",
            "_implementation",
            "implementation_address",
            "Proxy_implementation_address",
        ]

        return (
            await ProxyResolver._get_selector_implementations(
                selectors=selectors, **kwargs
            ),
            await ProxyResolver._get_storage_var_implementations(
                storage_vars=storage_vars, **kwargs
            ),
        )

    @staticmethod
    async def _get_selector_implementations(
        selectors: List[str], **kwargs
    ) -> List[int]:
        def _is_function(abi_entry_: Dict[str, Any]) -> bool:
            return abi_entry_["type"] == "function" and len(abi_entry_["inputs"]) == 0

        selector_implementations = []
        for abi_entry in kwargs["proxy_abi"]:
            if not _is_function(abi_entry) or abi_entry["name"] not in selectors:
                continue

            call = Call(
                to_addr=kwargs["proxy_address"],
                selector=get_selector_from_name(abi_entry["name"]),
                calldata=[],
            )
            (implementation,) = await kwargs["client"].call_contract(call)

            if implementation != 0:
                selector_implementations.append(implementation)
        return selector_implementations

    @staticmethod
    async def _get_storage_var_implementations(
        storage_vars: List[str], **kwargs
    ) -> List[int]:
        storage_var_implementations = []
        for storage_var in storage_vars:
            implementation = await kwargs["client"].get_storage_at(
                contract_address=kwargs["proxy_address"],
                key=get_storage_var_address(storage_var),
            )
            if implementation != 0:
                storage_var_implementations.append(implementation)
        return storage_var_implementations


class ContractClassResolver:
    """
    Class for resolving Class of a Contract.
    """

    @staticmethod
    async def resolve(
        implementations: List[int], client: Client
    ) -> Optional[DeclaredContract]:
        """
        Get class from possible implementations.
        Any number of them can be invalid implementations.
        When 2 or more implementations are an actual implementation (class_hash / address)
        of a contract on StarkNet, None is returned.

        :param implementations: List of possible implementations (class_hashes / addresses).
        :param client: Client used for resolving contract class.
        :raises ContractNotFoundError: When contract was not found at address.
        :return: Class at address or None.
        """
        found_contract_class = None

        for implementation in implementations:
            contract_class = await ContractClassResolver._try_resolve(
                implementation=implementation, client=client
            )
            if (
                found_contract_class
                and contract_class
                and found_contract_class != contract_class
            ):
                return None

            found_contract_class = contract_class

        return found_contract_class

    @staticmethod
    async def _try_resolve(
        implementation: int, client: Client
    ) -> Optional[DeclaredContract]:
        """
        Given implementation, try to fetch the contract class first as a class_hash, then as an address.
        """
        contract_class = await ContractClassResolver._by_class_hash(
            class_hash=implementation, client=client
        )
        return contract_class or await ContractClassResolver._by_address(
            address=implementation, client=client
        )

    @staticmethod
    async def _by_class_hash(
        class_hash: int, client: Client
    ) -> Optional[DeclaredContract]:
        try:
            return await client.get_class_by_hash(class_hash)
        except ClientError as err:
            if not (
                "is not declared" in err.message
                or err.code == RPC_CLASS_HASH_NOT_FOUND_ERROR
            ):
                raise err

    @staticmethod
    async def _by_address(address: int, client: Client) -> Optional[DeclaredContract]:
        try:
            return await ContractClassResolver.get_class_at(address, client)
        except ContractNotFoundError:
            pass

    @staticmethod
    async def get_class_at(address: Address, client: Client) -> DeclaredContract:
        """
        Get class at address.

        :param address: Address of the contract whose class is to be returned.
        :param client: Client used for fetching contract class.
        :raises ContractNotFoundError: When contract was not found at address.
        :return: Class at address.
        """
        try:
            contract_class_hash = await client.get_class_hash_at(
                contract_address=address
            )
            contract_class = await client.get_class_by_hash(
                class_hash=contract_class_hash
            )
        except ClientError as err:
            if "is not deployed" in err.message or err.code in [
                RPC_CONTRACT_NOT_FOUND_ERROR,
                RPC_CLASS_HASH_NOT_FOUND_ERROR,
            ]:
                raise ContractNotFoundError(address=address) from err
            raise err

        return contract_class
