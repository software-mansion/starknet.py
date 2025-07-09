import dataclasses
import re
from unittest.mock import Mock

import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.contract import Contract, DeclareResult
from starknet_py.net.client_models import InvokeTransactionV3
from starknet_py.net.models import DeclareV3
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.fixtures.misc import load_contract


@pytest.mark.asyncio
async def test_declare_deploy_v3(
    account,
    minimal_contract_class_hash: int,
):
    compiled_contract = load_contract("MinimalContract")["sierra"]

    declare_result = DeclareResult(
        _account=account,
        _client=account.client,
        _cairo_version=1,
        class_hash=minimal_contract_class_hash,
        compiled_contract=compiled_contract,
        hash=0,
        declare_transaction=Mock(spec=DeclareV3),
    )

    tip = 12345
    deploy_result = await declare_result.deploy_v3(
        resource_bounds=MAX_RESOURCE_BOUNDS, tip=tip
    )
    await deploy_result.wait_for_acceptance()

    assert isinstance(deploy_result.hash, int)
    assert deploy_result.hash != 0
    assert deploy_result.deployed_contract.address != 0
    transaction = await account.client.get_transaction(deploy_result.hash)
    assert isinstance(transaction, InvokeTransactionV3)
    assert transaction.tip == tip


@pytest.mark.asyncio
async def test_throws_on_wrong_abi(account, minimal_contract_class_hash: int):
    compiled_contract = load_contract("MinimalContract")["sierra"]

    declare_result = DeclareResult(
        _account=account,
        _client=account.client,
        _cairo_version=1,
        class_hash=minimal_contract_class_hash,
        compiled_contract=compiled_contract,
        hash=0,
        declare_transaction=Mock(spec=DeclareV3),
    )

    compiled_contract = compiled_contract.replace('"abi":[', '"api": ')

    declare_result = dataclasses.replace(
        declare_result, compiled_contract=compiled_contract
    )
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Contract's ABI can't be converted to format List[Dict]. "
            "Make sure provided compiled_contract is correct."
        ),
    ):
        await declare_result.deploy_v3(resource_bounds=MAX_RESOURCE_BOUNDS)


@pytest.mark.asyncio
async def test_deploy_contract_v3(account, hello_starknet_class_hash: int):
    compiled_contract = load_contract("HelloStarknet")["sierra"]
    abi = create_sierra_compiled_contract(
        compiled_contract=compiled_contract
    ).parsed_abi

    tip = 12345
    deploy_result = await Contract.deploy_contract_v3(
        class_hash=hello_starknet_class_hash,
        account=account,
        abi=abi,
        resource_bounds=MAX_RESOURCE_BOUNDS,
        tip=tip,
    )
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract

    assert isinstance(contract.address, int)
    assert len(contract.functions) != 0

    transaction = await account.client.get_transaction(tx_hash=deploy_result.hash)
    assert isinstance(transaction, InvokeTransactionV3)
    assert transaction.tip == tip

    class_hash = await account.client.get_class_hash_at(
        contract_address=contract.address
    )
    assert class_hash == hello_starknet_class_hash
