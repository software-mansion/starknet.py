import sys

import pytest

from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.utils.constructor_args_translator import translate_constructor_args


@pytest.mark.asyncio
async def test_default_deploy_with_class_hash(account, map_class_hash):
    deployer = Deployer()

    contract_deployment = deployer.create_contract_deployment(class_hash=map_class_hash)

    deploy_invoke_tx = await account.sign_invoke_v3(
        contract_deployment.call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    assert isinstance(contract_deployment.address, int)
    assert contract_deployment.address != 0


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
@pytest.mark.parametrize("calldata", [[10, 1, 2, 3, 3, 1, 2, 3, 12, 99]])
async def test_constructor_arguments_contract_deploy_without_abi(
    account,
    constructor_with_arguments_class_hash,
    calldata,
):
    deployer = Deployer(account_address=account.address)

    deploy_call, contract_address = deployer.create_contract_deployment(
        class_hash=constructor_with_arguments_class_hash,
        calldata=calldata,
    )

    deploy_invoke_transaction = await account.sign_invoke_v3(
        deploy_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    contract = await Contract.from_address(address=contract_address, provider=account)

    result = (await contract.functions["get"].call(block_number="latest"))[0]
    unwrapped_result = (result[0], result[1], result[2], dict(result[3]))
    expected_result = (
        10,
        (1, (2, 3)),
        sum([1, 2, 3]),
        {"value": 12, "nested_struct": {"value": 99}},
    )
    assert unwrapped_result == expected_result


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
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
    constructor_with_arguments_abi,
    constructor_with_arguments_class_hash,
    calldata,
):
    deployer = Deployer(account_address=account.address)

    deploy_call, contract_address = deployer.create_contract_deployment(
        class_hash=constructor_with_arguments_class_hash,
        abi=constructor_with_arguments_abi,
        calldata=calldata,
    )

    deploy_invoke_transaction = await account.sign_invoke_v3(
        deploy_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    contract = Contract(
        address=contract_address,
        abi=constructor_with_arguments_abi,
        provider=account,
    )

    result = (await contract.functions["get"].call(block_number="latest"))[0]
    unwarpped_result = (result[0], result[1], result[2], dict(result[3]))
    assert unwarpped_result == (
        10,
        (1, (2, 3)),
        sum([1, 2, 3]),
        {"value": 12, "nested_struct": {"value": 99}},
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
async def test_throws_when_calldata_provided_without_abi(
    account,
    constructor_with_arguments_class_hash,
    calldata,
):
    deployer = Deployer(account_address=account.address)

    with pytest.raises(
        ValueError,
        match="Argument calldata was provided without an ABI. It cannot be serialized.",
    ):
        deployer.create_contract_deployment(
            class_hash=constructor_with_arguments_class_hash, calldata=calldata
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

    deploy_invoke_tx = await account.sign_invoke_v3(
        deploy_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    tx_receipt = await account.client.get_transaction_receipt(resp.transaction_hash)
    address_from_event = tx_receipt.events[0].data[0]

    assert computed_address == address_from_event


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
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
    constructor_with_arguments_abi,
    constructor_with_arguments_class_hash,
    calldata,
):
    deployer = Deployer(account_address=account.address)

    raw_calldata = translate_constructor_args(
        abi=constructor_with_arguments_abi, constructor_args=calldata
    )

    (
        deploy_call,
        contract_address,
    ) = deployer.create_contract_deployment_raw(
        class_hash=constructor_with_arguments_class_hash,
        raw_calldata=raw_calldata,
    )

    deploy_invoke_transaction = await account.sign_invoke_v3(
        deploy_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    assert isinstance(contract_address, int)
    assert contract_address != 0


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_create_deployment_call_raw_supports_seed_0(
    account,
    constructor_with_arguments_abi,
    constructor_with_arguments_class_hash,
):
    sample_calldata = {
        # the transactions have to be different for each account
        "single_value": 20 if isinstance(account.client, FullNodeClient) else 30,
        "tuple": (1, (2, 3)),
        "arr": [1, 2, 3],
        "dict": {"value": 12, "nested_struct": {"value": 99}},
    }
    deployer = Deployer()

    raw_calldata = translate_constructor_args(
        abi=constructor_with_arguments_abi,
        constructor_args=sample_calldata,
    )

    expected_address = compute_address(
        class_hash=constructor_with_arguments_class_hash,
        constructor_calldata=raw_calldata,
        salt=1,
    )

    (
        deploy_call,
        contract_address,
    ) = deployer.create_contract_deployment_raw(
        class_hash=constructor_with_arguments_class_hash,
        raw_calldata=raw_calldata,
        salt=1,
    )

    deploy_invoke_transaction = await account.sign_invoke_v3(
        deploy_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    assert isinstance(contract_address, int)
    assert (
        contract_address == expected_address
    ), f"Expected address {expected_address}, got {contract_address}."
