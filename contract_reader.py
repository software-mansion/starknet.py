from typing import Dict, Optional, Union, List, Dict as TypingDict

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.storage import get_storage_var_address
from starknet_py.net.client import Client
from starknet_py.net.client_models import Call
from starknet_py.net.models import Address
from starknet_py.proxy.contract_abi_resolver import ContractAbiResolver
from starknet_py.net.udc_deployer import Deployer

class ContractData:
    @staticmethod
    def from_abi(address: int, abi: list, cairo_version: int) -> 'ContractData':
        # Implement this method as needed
        pass

class ContractFunction:
    def __init__(self, name, abi, contract_data, client, account, cairo_version, interface_name=None):
        # Implement this constructor as needed
        pass

class ProxyConfig:
    pass

def prepare_proxy_config(proxy_config) -> ProxyConfig:
    # Implement this function as needed
    pass

def parse_address(address: str) -> int:
    # Implement a method to parse or convert addresses to integers if needed
    return int(address, 16)

class Contract:
    def __init__(
        self,
        address: int,
        abi: list,
        provider: Union[BaseAccount, Client],
        *,
        cairo_version: int = 1,
    ):
        client, account = _unpack_provider(provider)

        self.account: Optional[BaseAccount] = account
        self.client: Client = client
        self.data = ContractData.from_abi(address, abi, cairo_version)

        try:
            self._functions = self._make_functions(
                contract_data=self.data,
                client=self.client,
                account=self.account,
                cairo_version=cairo_version,
            )
        except ValidationError as exc:
            raise ValueError(
                "Make sure valid ABI is used to create a Contract instance"
            ) from exc

    @property
    def functions(self) -> Dict[str, ContractFunction]:
        return self._functions

    @property
    def address(self) -> int:
        return self.data.address

    @staticmethod
    async def from_address(
        address: str,
        provider: Union[BaseAccount, Client] = None,
        proxy_config: Union[bool, ProxyConfig] = False,
    ) -> 'Contract':
        client, account = _unpack_provider(provider)
        address = parse_address(address)
        proxy_config = Contract._create_proxy_config(proxy_config)

        abi, cairo_version = await ContractAbiResolver(
            address=address, client=client, proxy_config=proxy_config
        ).resolve()

        return Contract(
            address=address,
            abi=abi,
            provider=account or client,
            cairo_version=cairo_version,
        )

    @staticmethod
    async def declare_v1(
        account: BaseAccount,
        compiled_contract: str,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> 'DeclareResult':
        declare_tx = await account.sign_declare_v1(
            compiled_contract=compiled_contract,
            nonce=nonce,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
        )
        return await _declare_contract(
            declare_tx, account, compiled_contract, cairo_version=0
        )

    @staticmethod
    async def declare_v2(
        account: BaseAccount,
        compiled_contract: str,
        *,
        compiled_contract_casm: Optional[str] = None,
        compiled_class_hash: Optional[int] = None,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> 'DeclareResult':
        compiled_class_hash = _extract_compiled_class_hash(
            compiled_contract_casm, compiled_class_hash
        )
        declare_tx = await account.sign_declare_v2(
            compiled_contract=compiled_contract,
            compiled_class_hash=compiled_class_hash,
            nonce=nonce,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
        )
        return await _declare_contract(
            declare_tx, account, compiled_contract, cairo_version=1
        )

    @staticmethod
    async def declare_v3(
        account: BaseAccount,
        compiled_contract: str,
        *,
        compiled_contract_casm: Optional[str] = None,
        compiled_class_hash: Optional[int] = None,
        nonce: Optional[int] = None,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        auto_estimate: bool = False,
    ) -> 'DeclareResult':
        compiled_class_hash = _extract_compiled_class_hash(
            compiled_contract_casm, compiled_class_hash
        )
        declare_tx = await account.sign_declare_v3(
            compiled_contract=compiled_contract,
            compiled_class_hash=compiled_class_hash,
            nonce=nonce,
            l1_resource_bounds=l1_resource_bounds,
            auto_estimate=auto_estimate,
        )
        return await _declare_contract(
            declare_tx, account, compiled_contract, cairo_version=1
        )

    @staticmethod
    async def deploy_contract_v1(
        account: BaseAccount,
        class_hash: Hash,
        abi: List,
        constructor_args: Optional[Union[List, Dict]] = None,
        *,
        deployer_address: Address = DEFAULT_DEPLOYER_ADDRESS,
        cairo_version: int = 0,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        salt: Optional[int] = None,
        unique: bool = True,
    ) -> 'DeployResult':
        deployer = Deployer(
            deployer_address=deployer_address,
            account_address=account.address if unique else None,
        )
        deploy_call, address = deployer.create_contract_deployment(
            class_hash=class_hash,
            salt=salt,
            abi=abi,
            calldata=constructor_args,
            cairo_version=cairo_version,
        )
        res = await account.execute_v1(
            calls=deploy_call,
            nonce=nonce,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
        )
        deployed_contract = Contract(
            provider=account, address=address, abi=abi, cairo_version=cairo_version
        )
        deploy_result = DeployResult(
            hash=res.transaction_hash,
            _client=account.client,
            deployed_contract=deployed_contract,
        )
        return deploy_result

    @staticmethod
    async def deploy_contract_v3(
        account: BaseAccount,
        class_hash: Hash,
        abi: List,
        constructor_args: Optional[Union[List, Dict]] = None,
        *,
        deployer_address: Address = DEFAULT_DEPLOYER_ADDRESS,
        cairo_version: int = 1,
        nonce: Optional[int] = None,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        auto_estimate: bool = False,
        salt: Optional[int] = None,
        unique: bool = True,
    ) -> 'DeployResult':
        deployer = Deployer(
            deployer_address=deployer_address,
            account_address=account.address if unique else None,
        )
        deploy_call, address = deployer.create_contract_deployment(
            class_hash=class_hash,
            salt=salt,
            abi=abi,
            calldata=constructor_args,
            cairo_version=cairo_version,
        )
        res = await account.execute_v3(
            calls=deploy_call,
            nonce=nonce,
            l1_resource_bounds=l1_resource_bounds,
            auto_estimate=auto_estimate,
        )
        deployed_contract = Contract(
            provider=account, address=address, abi=abi, cairo_version=cairo_version
        )
        deploy_result = DeployResult(
            hash=res.transaction_hash,
            _client=account.client,
            deployed_contract=deployed_contract,
        )
        return deploy_result

    @classmethod
    def _make_functions(
        cls,
        contract_data: ContractData,
        client: Client,
        account: Optional[BaseAccount],
        cairo_version: int = 1,
    ) -> Dict[str, ContractFunction]:
        repository = {}
        implemented_interfaces = [
            entry["interface_name"]
            for entry in contract_data.abi
            if entry["type"] == IMPL_ENTRY
        ]
        for abi_entry in contract_data.abi:
            if abi_entry["type"] in [FUNCTION_ENTRY, L1_HANDLER_ENTRY]:
                name = abi_entry["name"]
                repository[name] = ContractFunction(
                    name=name,
                    abi=abi_entry,
                    contract_data=contract_data,
                    client=client,
                    account=account,
                    cairo_version=cairo_version,
                )
        
            if (
                abi_entry["type"] == INTERFACE_ENTRY
                and abi_entry["name"] in implemented_interfaces
            ):
                repository[abi_entry["name"]] = ContractFunction(
                    name=abi_entry["name"],
                    abi=abi_entry,
                    contract_data=contract_data,
                    client=client,
                    account=account,
                    cairo_version=cairo_version,
                    interface_name=abi_entry["name"],
                )
        return repository

    @staticmethod
    def _create_proxy_config(proxy_config: Union[bool, ProxyConfig]) -> ProxyConfig:
        if isinstance(proxy_config, bool):
            return ProxyConfig() if proxy_config else None
        return proxy_config
