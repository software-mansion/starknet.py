import pytest

from starknet_py.contract import Contract, ContractFunction
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_DIR

mock_contracts_base_path = CONTRACTS_DIR
base_source_code = (CONTRACTS_DIR / "base.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_deploy_tx(gateway_account_client, map_source_code):
    result = await Contract.deploy(
        client=gateway_account_client, compilation_source=map_source_code
    )
    result = await result.wait_for_acceptance()
    result = result.deployed_contract

    assert isinstance(result.functions["get"], ContractFunction)
    assert isinstance(result.functions["put"], ContractFunction)


@pytest.mark.asyncio
async def test_deploy_with_search_path(gateway_account_client):
    result = await Contract.deploy(
        client=gateway_account_client,
        compilation_source=base_source_code,
        search_paths=[str(mock_contracts_base_path)],
    )
    await result.wait_for_acceptance()

    result = await Contract.deploy(
        client=gateway_account_client,
        compilation_source=base_source_code,
        search_paths=[str(mock_contracts_base_path)],
    )
    result = await result.wait_for_acceptance()
    result = result.deployed_contract
    assert isinstance(result.functions["put"], ContractFunction)


constructor_with_arguments_source = (
    CONTRACTS_DIR / "constructor_with_arguments.cairo"
).read_text("utf-8")
