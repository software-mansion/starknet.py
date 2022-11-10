# pylint: disable=redefined-outer-name

import pytest
import pytest_asyncio
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.contract import Contract, DeployResult
from starknet_py.tests.e2e.fixtures.misc import read_contract
from starknet_py.transactions.declare import make_declare_tx


@pytest.fixture(
    params=["argent_proxy_compiled.json", "oz_proxy_compiled.json"],
    scope="session",
)
def compiled_proxy(request) -> str:
    """
    Returns source code of compiled proxy contract
    """
    return read_contract(request.param)


@pytest.fixture(scope="session")
def custom_proxy() -> str:
    """
    Returns compiled source code of a custom proxy
    """
    return read_contract("oz_proxy_custom_compiled.json")


@pytest.fixture(scope="session")
def old_proxy() -> str:
    """
    Returns compiled (using starknet-compile 0.8.1) source code of OpenZeppelin's proxy using address and delegate_call.
    """
    return read_contract("_oz_proxy_address_0.8.1_compiled.json")


@pytest_asyncio.fixture(
    params=[
        ("oz_proxy_compiled.json", "map_compiled.json"),
        ("argent_proxy_compiled.json", "map_compiled.json"),
    ]
)
async def deploy_proxy_to_contract_oz_argent(
    request, gateway_account_client
) -> DeployResult:
    """
    Declares a contract and deploys a proxy (OZ, Argent) pointing to that contract.
    """
    compiled_proxy_name, compiled_contract_name = request.param
    return await deploy_proxy_to_contract(
        compiled_proxy_name, compiled_contract_name, gateway_account_client
    )


@pytest_asyncio.fixture(params=[("oz_proxy_custom_compiled.json", "map_compiled.json")])
async def deploy_proxy_to_contract_custom(
    request, gateway_account_client
) -> DeployResult:
    """
    Declares a contract and deploys a custom proxy pointing to that contract.
    """
    compiled_proxy_name, compiled_contract_name = request.param
    return await deploy_proxy_to_contract(
        compiled_proxy_name, compiled_contract_name, gateway_account_client
    )


async def deploy_proxy_to_contract(
    compiled_proxy_name, compiled_contract_name, gateway_account_client
) -> DeployResult:
    """
    Declares a contract and deploys a proxy pointing to that contract.
    """
    compiled_proxy = read_contract(compiled_proxy_name)
    compiled_contract = read_contract(compiled_contract_name)

    declare_tx = make_declare_tx(compiled_contract=compiled_contract)
    declare_result = await gateway_account_client.declare(declare_tx)

    implementation_key = (
        "implementation_hash"
        if "implementation_hash" in compiled_proxy
        else "implementation"
    )
    deployment_result = await Contract.deploy(
        compiled_contract=compiled_proxy,
        constructor_args={
            implementation_key: declare_result.class_hash,
            "selector": get_selector_from_name("put"),
            "calldata": [69, 420],
        },
        client=gateway_account_client,
    )
    await deployment_result.wait_for_acceptance()
    return deployment_result
