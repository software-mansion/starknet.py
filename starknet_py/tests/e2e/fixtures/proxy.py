# pylint: disable=redefined-outer-name

import pytest
import pytest_asyncio
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.contract import Contract, DeployResult
from starknet_py.net import AccountClient
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_PRECOMPILED_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.fixture(
    params=["argent_proxy_compiled.json", "oz_proxy_compiled.json"],
    scope="session",
)
def compiled_proxy(request) -> str:
    """
    Returns source code of compiled proxy contract.
    """
    return read_contract(request.param)


@pytest.fixture(scope="session")
def custom_proxy() -> str:
    """
    Returns compiled source code of a custom proxy.
    """
    return read_contract("oz_proxy_custom_compiled.json")


@pytest.fixture(scope="session")
def old_proxy() -> str:
    """
    Returns compiled (using starknet-compile 0.8.1) source code of OpenZeppelin's proxy using address and delegate_call.
    """
    return read_contract(
        "oz_proxy_address_0.8.1_compiled.json", directory=CONTRACTS_PRECOMPILED_DIR
    )


@pytest_asyncio.fixture(
    params=[
        ("oz_proxy_compiled.json", "map_compiled.json"),
        ("argent_proxy_compiled.json", "map_compiled.json"),
    ]
)
async def deploy_proxy_to_contract_oz_argent(
    request, new_gateway_account_client: AccountClient
) -> DeployResult:
    """
    Declares a contract and deploys a proxy (OZ, Argent) pointing to that contract.
    """
    compiled_proxy_name, compiled_contract_name = request.param
    return await deploy_proxy_to_contract(
        compiled_proxy_name, compiled_contract_name, new_gateway_account_client
    )


@pytest_asyncio.fixture(params=[("oz_proxy_custom_compiled.json", "map_compiled.json")])
async def deploy_proxy_to_contract_custom(
    request, new_gateway_account_client: AccountClient
) -> DeployResult:
    """
    Declares a contract and deploys a custom proxy pointing to that contract.
    """
    compiled_proxy_name, compiled_contract_name = request.param
    return await deploy_proxy_to_contract(
        compiled_proxy_name, compiled_contract_name, new_gateway_account_client
    )


@pytest_asyncio.fixture(
    params=[("oz_proxy_exposed_compiled.json", "map_compiled.json")]
)
async def deploy_proxy_to_contract_exposed(
    request, new_gateway_account_client: AccountClient
) -> DeployResult:
    """
    Declares a contract and deploys a custom proxy pointing to that contract.
    """
    compiled_proxy_name, compiled_contract_name = request.param
    return await deploy_proxy_to_contract(
        compiled_proxy_name, compiled_contract_name, new_gateway_account_client
    )


async def deploy_proxy_to_contract(
    compiled_proxy_name: str,
    compiled_contract_name: str,
    gateway_account_client: AccountClient,
) -> DeployResult:
    """
    Declares a contract and deploys a proxy pointing to that contract.
    """
    compiled_proxy = read_contract(compiled_proxy_name)
    compiled_contract = read_contract(compiled_contract_name)

    declare_tx = await gateway_account_client.sign_declare_transaction(
        compiled_contract=compiled_contract, max_fee=MAX_FEE
    )
    declare_result = await gateway_account_client.declare(declare_tx)
    await gateway_account_client.wait_for_tx(declare_result.transaction_hash)

    declare_proxy_result = await Contract.declare(
        account=gateway_account_client,
        compiled_contract=compiled_proxy,
        max_fee=MAX_FEE,
    )
    await declare_proxy_result.wait_for_acceptance()
    deploy_result = await declare_proxy_result.deploy(
        constructor_args=[
            declare_result.class_hash,
            get_selector_from_name("put"),
            [69, 420],
        ],
        max_fee=MAX_FEE,
    )
    await deploy_result.wait_for_acceptance()
    return deploy_result
