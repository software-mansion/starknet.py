import sys

import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import load_contract
from starknet_py.utils.constructor_args_translator import translate_constructor_args


@pytest.mark.asyncio
async def test_default_deploy_with_class_hash(account, map_class_hash):
    deployer = Deployer()

    contract_deployment = deployer.create_contract_deployment(class_hash=map_class_hash)

    deploy_invoke_tx = await account.sign_invoke_v1(
        contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    assert isinstance(contract_deployment.address, int)
    assert contract_deployment.address != 0


@pytest.mark.asyncio
async def test_throws_when_calldata_provided_without_abi(map_class_hash):
    deployer = Deployer()

    with pytest.raises(ValueError, match="calldata was provided without an ABI."):
        deployer.create_contract_deployment(
            class_hash=map_class_hash, calldata=[12, 34]
        )


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_throws_when_calldata_not_provided():
    contract = create_sierra_compiled_contract(
        compiled_contract=load_contract("ConstructorWithArguments")["sierra"]
    )

    deployer = Deployer()

    with pytest.raises(
        ValueError,
        match="Provided contract has a constructor and no arguments were provided.",
    ):
        deployer.create_contract_deployment(
            class_hash=1234, abi=contract.parsed_abi, cairo_version=1
        )


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "calldata",
    [
        [10, (1, (2, 3)), [1, 2, 3], {"value": 12, "nested_struct": {"value": 99}}],
        {
            "single_value": 10,
            "tuple": (1, (2, 3)),
            "arr": [1, 2, 3],
            "dict": {"value": 12, "nested_struct": {"value": 99}},
        },
    ],
)
async def test_constructor_arguments_contract_deploy(
    account,
    cairo1_constructor_with_arguments_class_hash,
    calldata,
):
    contract = create_sierra_compiled_contract(
        compiled_contract=load_contract("ConstructorWithArguments")["sierra"]
    )

    deployer = Deployer(account_address=account.address)

    deploy_call, contract_address = deployer.create_contract_deployment(
        class_hash=cairo1_constructor_with_arguments_class_hash,
        abi=contract.parsed_abi,
        calldata=calldata,
        cairo_version=1,
    )

    deploy_invoke_transaction = await account.sign_invoke_v1(
        deploy_call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    contract = Contract(
        address=contract_address,
        abi=contract.parsed_abi,
        provider=account,
        cairo_version=1,
    )

    result = (await contract.functions["get"].call(block_number="latest"))[0]
    unwarpped_result = (result[0], result[1], result[2], dict(result[3]))
    assert unwarpped_result == (
        10,
        (1, (2, 3)),
        sum([1, 2, 3]),
        {"value": 12, "nested_struct": {"value": 99}},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "salt, pass_account_address", [(1, True), (2, False), (None, True), (None, False)]
)
async def test_address_computation(salt, pass_account_address, account, map_class_hash):
    deployer = Deployer(
        account_address=account.address if pass_account_address else None
    )
    if isinstance(salt, int) and isinstance(account.client, FullNodeClient):
        # transactions have to be different for each account
        salt += 1

    deploy_call, computed_address = deployer.create_contract_deployment(
        class_hash=map_class_hash,
        salt=salt,
    )

    deploy_invoke_tx = await account.sign_invoke_v1(deploy_call, max_fee=MAX_FEE)
    resp = await account.client.send_transaction(deploy_invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    tx_receipt = await account.client.get_transaction_receipt(resp.transaction_hash)
    address_from_event = tx_receipt.events[0].data[0]

    assert computed_address == address_from_event


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "calldata",
    [
        [10, (1, (2, 3)), [1, 2, 3], {"value": 12, "nested_struct": {"value": 99}}],
        {
            "single_value": 10,
            "tuple": (1, (2, 3)),
            "arr": [1, 2, 3],
            "dict": {"value": 12, "nested_struct": {"value": 99}},
        },
    ],
)
async def test_create_deployment_call_raw(
    account,
    cairo1_constructor_with_arguments_class_hash,
    calldata,
):
    contract = create_sierra_compiled_contract(
        compiled_contract=load_contract("ConstructorWithArguments")["sierra"]
    )

    deployer = Deployer(account_address=account.address)

    raw_calldata = translate_constructor_args(
        abi=contract.parsed_abi, constructor_args=calldata, cairo_version=1
    )

    (
        deploy_call,
        contract_address,
    ) = deployer.create_contract_deployment_raw(
        class_hash=cairo1_constructor_with_arguments_class_hash,
        raw_calldata=raw_calldata,
    )

    deploy_invoke_transaction = await account.sign_invoke_v1(
        deploy_call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    assert isinstance(contract_address, int)
    assert contract_address != 0


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_create_deployment_call_raw_supports_seed_0(
    account,
    cairo1_constructor_with_arguments_class_hash,
):
    contract = create_sierra_compiled_contract(
        compiled_contract=load_contract("ConstructorWithArguments")["sierra"]
    )

    sample_calldata = {
        # the transactions have to be different for each account
        "single_value": 20 if isinstance(account.client, FullNodeClient) else 30,
        "tuple": (1, (2, 3)),
        "arr": [1, 2, 3],
        "dict": {"value": 12, "nested_struct": {"value": 99}},
    }
    deployer = Deployer()

    raw_calldata = translate_constructor_args(
        abi=contract.parsed_abi,
        constructor_args=sample_calldata,
        cairo_version=1,
    )

    expected_address = compute_address(
        class_hash=cairo1_constructor_with_arguments_class_hash,
        constructor_calldata=raw_calldata,
        salt=1,
    )

    (
        deploy_call,
        contract_address,
    ) = deployer.create_contract_deployment_raw(
        class_hash=cairo1_constructor_with_arguments_class_hash,
        raw_calldata=raw_calldata,
        salt=1,
    )

    deploy_invoke_transaction = await account.sign_invoke_v1(
        deploy_call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    assert isinstance(contract_address, int)
    assert (
        contract_address == expected_address
    ), f"Expected address {expected_address}, got {contract_address}."
