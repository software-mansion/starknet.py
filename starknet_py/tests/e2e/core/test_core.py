from typing import cast

import pytest

from starknet_py.contract import Contract, PreparedFunctionCall
from starknet_py.net.account.account import Account
from starknet_py.net.account.account_deployment_result import AccountDeploymentResult
from starknet_py.net.client_models import (
    DeclareTransaction,
    DeclareTransactionResponse,
    EstimatedFee,
)
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


@pytest.mark.asyncio
async def test_declare_account(
    core_pre_deployed_account,
    core_declare_account_response: DeclareTransactionResponse,
):
    await core_pre_deployed_account.client.wait_for_tx(
        core_declare_account_response.transaction_hash
    )

    declare_tx = cast(
        DeclareTransaction,
        await core_pre_deployed_account.client.get_transaction(
            core_declare_account_response.transaction_hash
        ),
    )

    assert core_declare_account_response.class_hash != 0
    assert core_declare_account_response.class_hash == declare_tx.class_hash


@pytest.mark.asyncio
async def test_deploy_account(
    core_deploy_account_response: AccountDeploymentResult,
):
    await core_deploy_account_response.wait_for_acceptance()

    assert core_deploy_account_response.account.address != 0


@pytest.mark.asyncio
async def test_declare_v1(core_declare_map_response: DeclareTransactionResponse):
    assert core_declare_map_response.class_hash != 0


@pytest.mark.asyncio
async def test_declare_v2(
    core_pre_deployed_account, sierra_minimal_compiled_contract_and_class_hash
):
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash

    declare_tx = await core_pre_deployed_account.sign_declare_v2_transaction(
        compiled_contract=compiled_contract,
        compiled_class_hash=compiled_class_hash,
        max_fee=MAX_FEE,
    )
    resp = await core_pre_deployed_account.client.declare(declare_tx)
    await core_pre_deployed_account.client.wait_for_tx(resp.transaction_hash)

    assert resp.class_hash != 0


@pytest.mark.asyncio
async def test_deployer(core_map_contract: Contract):
    assert core_map_contract.address != 0


@pytest.mark.asyncio
async def test_contract(core_map_contract: Contract):
    prepared_tx: PreparedFunctionCall = core_map_contract.functions["put"].prepare(
        key=10, value=20
    )

    estimated_fee = await prepared_tx.estimate_fee()

    assert isinstance(estimated_fee, EstimatedFee)
    assert estimated_fee.overall_fee > 0

    resp = await prepared_tx.invoke(max_fee=int(estimated_fee.overall_fee * 1.5))
    await resp.wait_for_acceptance()

    (value,) = await core_map_contract.functions["get"].call(key=10)

    assert value == 20


@pytest.mark.asyncio
async def test_multicall(
    core_map_contract: Contract, core_pre_deployed_account: Account
):
    calls = [
        core_map_contract.functions["put"].prepare(key=i, value=i * 10)
        for i in range(5)
    ]

    resp = await core_pre_deployed_account.execute(calls, max_fee=MAX_FEE)
    await core_pre_deployed_account.client.wait_for_tx(resp.transaction_hash)

    for i in range(5):
        (value,) = await core_map_contract.functions["get"].call(key=i)
        assert value == i * 10
