# pylint: disable=redefined-outer-name

import pytest
import pytest_asyncio

from starknet_py.constants import FEE_CONTRACT_ADDRESS, DEVNET_FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.tests.e2e.conftest import contracts_dir


@pytest.fixture(
    scope="module", params=["deploy_map_contract", "new_deploy_map_contract"]
)
def map_contract(request) -> Contract:
    """
    Returns account contracts using old and new account versions
    """
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="module")
def map_source_code() -> str:
    """
    Returns source code of the map contract
    """
    return (contracts_dir / "map.cairo").read_text("utf-8")


@pytest.fixture(scope="module")
def erc20_source_code() -> str:
    """
    Returns source code of the erc20 contract
    """
    return (contracts_dir / "erc20.cairo").read_text("utf-8")


@pytest_asyncio.fixture(name="deploy_map_contract", scope="module")
async def deploy_map_contract(
    gateway_account_client: AccountClient, map_source_code: str
) -> Contract:
    """
    Deploys map contract and returns its instance
    """
    deployment_result = await Contract.deploy(
        client=gateway_account_client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


@pytest_asyncio.fixture(name="new_deploy_map_contract", scope="module")
async def new_deploy_map_contract(
    new_gateway_account_client: AccountClient, map_source_code: str
) -> Contract:
    """
    Deploys new map contract and returns its instance
    """
    deployment_result = await Contract.deploy(
        client=new_gateway_account_client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


@pytest_asyncio.fixture(name="erc20_contract", scope="module")
async def deploy_erc20_contract(
    gateway_account_client: AccountClient, erc20_source_code: str
) -> Contract:
    """
    Deploys erc20 contract and returns its instance
    """
    deployment_result = await Contract.deploy(
        client=gateway_account_client, compilation_source=erc20_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


@pytest.fixture(
    name="compiled_proxy",
    params=["argent_proxy_compiled.json", "oz_proxy_compiled.json"],
)
def compiled_proxy(request) -> str:
    """
    Returns source code of compiled proxy contract
    """
    return (contracts_dir / request.param).read_text("utf-8")


@pytest.fixture(scope="module")
def fee_contract(pytestconfig, new_gateway_account_client: AccountClient) -> Contract:
    """
    Returns an instance of the fee contract. It is used to transfer tokens
    """
    abi = [
        {
            "inputs": [
                {"name": "recipient", "type": "felt"},
                {"name": "amount", "type": "Uint256"},
            ],
            "name": "transfer",
            "outputs": [{"name": "success", "type": "felt"}],
            "type": "function",
        },
        {
            "members": [
                {"name": "low", "offset": 0, "type": "felt"},
                {"name": "high", "offset": 1, "type": "felt"},
            ],
            "name": "Uint256",
            "size": 2,
            "type": "struct",
        },
    ]

    address = (
        FEE_CONTRACT_ADDRESS
        if pytestconfig.getoption("--net") != "devnet"
        else DEVNET_FEE_CONTRACT_ADDRESS
    )

    return Contract(
        address=address,
        abi=abi,
        client=new_gateway_account_client,
    )


@pytest.fixture(name="balance_contract")
def fixture_balance_contract() -> str:
    """
    Returns compiled code of the balance.cairo contract
    """
    return (contracts_dir / "balance_compiled.json").read_text("utf-8")
