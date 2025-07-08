import sys
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.constants import ARGENT_V040_CLASS_HASH
from starknet_py.hash.address import compute_address
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    Call,
    DeclareTransactionV3,
    DeployAccountTransactionResponse,
    DeployAccountTransactionV3,
    EstimatedFee,
    InvokeTransactionV3,
    PriceUnit,
    ResourceBounds,
    ResourceBoundsMapping,
    SierraContractClass,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
)
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeclareV3, DeployAccountV3, InvokeV3
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.accounts import AccountPrerequisites
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_balance_throws_when_token_not_specified(account):
    modified_account = Account(
        address=account.address,
        client=FullNodeClient(node_url="custom.net/rpc"),
        key_pair=KeyPair(1, 2),
        chain=cast(StarknetChainId, 1),
    )
    with pytest.raises(
        ValueError,
        match="Argument token_address must be specified when using a custom network.",
    ):
        await modified_account.get_balance()


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_balance_when_token_specified(account, erc20_contract):
    balance = await account.get_balance(erc20_contract.address)

    assert balance == 200


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_estimated_fee_greater_than_zero(account, erc20_contract):
    estimated_fee = (
        await erc20_contract.functions["balance_of"]
        .prepare_invoke_v3(
            account.address, resource_bounds=ResourceBoundsMapping.init_with_zeros()
        )
        .estimate_fee(block_hash="latest")
    )

    assert estimated_fee.overall_fee > 0
    assert estimated_fee.calculate_overall_fee() == estimated_fee.overall_fee


@pytest.mark.asyncio
async def test_estimate_fee_for_declare_transaction(
    account, map_compiled_contract_and_class_hash
):
    (compiled_contract, class_hash) = map_compiled_contract_and_class_hash
    declare_tx = await account.sign_declare_v3(
        compiled_contract=compiled_contract,
        compiled_class_hash=class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    estimated_fee = await account.client.estimate_fee(tx=declare_tx)

    assert isinstance(estimated_fee.overall_fee, int)
    assert estimated_fee.overall_fee > 0
    assert estimated_fee.calculate_overall_fee() == estimated_fee.overall_fee


@pytest.mark.asyncio
async def test_account_estimate_fee_for_declare_transaction(
    account, map_compiled_contract_and_class_hash
):
    (compiled_contract, class_hash) = map_compiled_contract_and_class_hash
    declare_tx = await account.sign_declare_v3(
        compiled_contract=compiled_contract,
        compiled_class_hash=class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    estimated_fee = await account.estimate_fee(tx=declare_tx)

    assert estimated_fee.unit == PriceUnit.FRI
    assert isinstance(estimated_fee.overall_fee, int)
    assert estimated_fee.overall_fee > 0
    assert estimated_fee.calculate_overall_fee() == estimated_fee.overall_fee


@pytest.mark.asyncio
async def test_account_estimate_fee_for_transactions(account, map_contract):
    invoke_tx_1 = await account.sign_invoke_v3(
        calls=Call(map_contract.address, get_selector_from_name("put"), [3, 4]),
        resource_bounds=MAX_RESOURCE_BOUNDS,
        nonce=(await account.get_nonce()),
    )

    invoke_tx_2 = await account.sign_invoke_v3(
        calls=Call(map_contract.address, get_selector_from_name("put"), [5, 1]),
        resource_bounds=MAX_RESOURCE_BOUNDS,
        nonce=(await account.get_nonce() + 1),
    )

    estimated_fee = await account.estimate_fee(tx=[invoke_tx_1, invoke_tx_2])

    assert len(estimated_fee) == 2
    assert isinstance(estimated_fee[0], EstimatedFee)
    assert isinstance(estimated_fee[1], EstimatedFee)
    assert estimated_fee[0].unit == PriceUnit.FRI
    assert estimated_fee[1].unit == PriceUnit.FRI
    assert isinstance(estimated_fee[0].overall_fee, int)
    assert estimated_fee[0].overall_fee > 0
    assert estimated_fee[0].calculate_overall_fee() == estimated_fee[0].overall_fee


@pytest.mark.asyncio
@pytest.mark.parametrize("key, val", [(20, 20), (30, 30)])
async def test_sending_multicall(account, map_contract, key, val):
    calls = [
        map_contract.functions["put"].prepare_invoke_v3(key=10, value=10),
        map_contract.functions["put"].prepare_invoke_v3(key=key, value=val),
    ]

    res = await account.execute_v3(calls=calls, resource_bounds=MAX_RESOURCE_BOUNDS)
    await account.client.wait_for_tx(res.transaction_hash)
    (value,) = await map_contract.functions["get"].call(key=key)

    assert value == val


@pytest.mark.asyncio
async def test_rejection_reason_in_transaction_receipt(map_contract):
    with pytest.raises(
        ClientError,
        match="The transaction's resources don't cover validation or the minimal transaction fee",
    ):
        resource_bounds = ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=1, max_price_per_unit=1),
            l2_gas=ResourceBounds(max_amount=1, max_price_per_unit=1),
            l1_data_gas=ResourceBounds(max_amount=1, max_price_per_unit=1),
        )
        await map_contract.functions["put"].invoke_v3(
            key=10, value=20, resource_bounds=resource_bounds
        )


def test_sign_and_verify_offchain_message_fail(account, typed_data):
    signature = account.sign_message(typed_data)
    signature = [signature[0] + 1, signature[1]]
    result = account.verify_message(typed_data, signature)

    assert result is False


def test_sign_and_verify_offchain_message(account, typed_data):
    signature = account.sign_message(typed_data)
    result = account.verify_message(typed_data, signature)

    assert result is True


@pytest.mark.asyncio
async def test_get_class_hash_at(account, map_contract):
    class_hash = await account.client.get_class_hash_at(
        map_contract.address, block_hash="latest"
    )

    assert class_hash != 0


@pytest.mark.asyncio()
async def test_get_nonce(account, map_contract):
    nonce = await account.get_nonce()
    address = map_contract.address
    block = await account.client.get_block(block_number="latest")

    tx = await account.execute_v3(
        Call(
            to_addr=address, selector=get_selector_from_name("put"), calldata=[10, 20]
        ),
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await account.client.wait_for_tx(tx.transaction_hash)

    new_nonce = await account.get_nonce()
    new_nonce_latest_block = await account.get_nonce(block_number="latest")

    old_nonce = await account.get_nonce(block_number=block.block_number)

    assert isinstance(nonce, int) and isinstance(new_nonce, int)
    assert new_nonce == nonce + 1

    assert old_nonce == nonce
    assert new_nonce_latest_block == new_nonce


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "calls", [[Call(10, 20, [30])], [Call(10, 20, [30]), Call(40, 50, [60])]]
)
async def test_sign_invoke_v3(account, calls):
    signed_tx = await account.sign_invoke_v3(calls, resource_bounds=MAX_RESOURCE_BOUNDS)

    assert isinstance(signed_tx, InvokeV3)
    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) == 2
    assert signed_tx.resource_bounds == MAX_RESOURCE_BOUNDS
    assert signed_tx.version == 3


@pytest.mark.asyncio
async def test_sign_invoke_v3_auto_estimate(account, map_contract):
    signed_tx = await account.sign_invoke_v3(
        Call(map_contract.address, get_selector_from_name("put"), [3, 4]),
        auto_estimate=True,
    )

    assert isinstance(signed_tx, InvokeV3)
    assert signed_tx.version == 3

    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) == 2

    assert isinstance(signed_tx.resource_bounds, ResourceBoundsMapping)
    assert signed_tx.resource_bounds.l1_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l1_gas.max_price_per_unit > 0
    assert signed_tx.resource_bounds.l2_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l2_gas.max_price_per_unit > 0
    assert signed_tx.resource_bounds.l1_data_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l1_data_gas.max_price_per_unit > 0


@pytest.mark.asyncio
async def test_sign_declare_v3(
    account, sierra_minimal_compiled_contract_and_class_hash
):
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash
    signed_tx = await account.sign_declare_v3(
        compiled_contract,
        compiled_class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    assert isinstance(signed_tx, DeclareV3)
    assert signed_tx.version == 3
    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) == 2
    assert signed_tx.nonce is not None
    assert signed_tx.resource_bounds == MAX_RESOURCE_BOUNDS
    assert signed_tx.version == 3


@pytest.mark.asyncio
async def test_sign_declare_v3_auto_estimate(
    account, sierra_minimal_compiled_contract_and_class_hash
):
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash

    signed_tx = await account.sign_declare_v3(
        compiled_contract, compiled_class_hash, auto_estimate=True
    )

    assert isinstance(signed_tx, DeclareV3)
    assert signed_tx.version == 3

    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) == 2

    assert isinstance(signed_tx.resource_bounds, ResourceBoundsMapping)
    assert signed_tx.resource_bounds.l1_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l1_gas.max_price_per_unit > 0
    assert signed_tx.resource_bounds.l2_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l2_gas.max_price_per_unit > 0
    assert signed_tx.resource_bounds.l1_data_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l1_data_gas.max_price_per_unit > 0


@pytest.mark.asyncio
async def test_sign_deploy_account_v3(account):
    class_hash = 0x1234
    salt = 0x123
    calldata = [1, 2, 3]
    signed_tx = await account.sign_deploy_account_v3(
        class_hash,
        salt,
        resource_bounds=MAX_RESOURCE_BOUNDS,
        constructor_calldata=calldata,
    )

    assert isinstance(signed_tx, DeployAccountV3)
    assert signed_tx.version == 3

    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) == 2

    assert signed_tx.resource_bounds == MAX_RESOURCE_BOUNDS
    assert signed_tx.class_hash == class_hash
    assert signed_tx.contract_address_salt == salt
    assert signed_tx.constructor_calldata == calldata


@pytest.mark.asyncio
async def test_sign_deploy_account_v3_auto_estimate(
    account, account_with_validate_deploy_class_hash
):
    class_hash = account_with_validate_deploy_class_hash
    salt = 0x123
    calldata = [account.signer.public_key]
    signed_tx = await account.sign_deploy_account_v3(
        class_hash, salt, constructor_calldata=calldata, auto_estimate=True
    )

    assert isinstance(signed_tx, DeployAccountV3)
    assert signed_tx.version == 3

    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) == 2

    assert isinstance(signed_tx.resource_bounds, ResourceBoundsMapping)
    assert signed_tx.resource_bounds.l1_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l1_gas.max_price_per_unit > 0
    assert signed_tx.resource_bounds.l2_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l2_gas.max_price_per_unit > 0
    assert signed_tx.resource_bounds.l1_data_gas.max_amount >= 0
    assert signed_tx.resource_bounds.l1_data_gas.max_price_per_unit > 0


@pytest.mark.asyncio
async def test_deploy_account_v3(client, deploy_account_details_factory):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    deploy_result = await Account.deploy_account_v3(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await deploy_result.wait_for_acceptance()

    account = deploy_result.account

    assert isinstance(account, BaseAccount)
    assert account.address == address

    transaction = await client.get_transaction(tx_hash=deploy_result.hash)
    assert isinstance(transaction, DeployAccountTransactionV3)
    assert transaction.constructor_calldata == [key_pair.public_key]


@pytest.mark.asyncio
async def test_deploy_account_raises_on_incorrect_address(
    client, deploy_account_details_factory
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    with pytest.raises(
        ValueError,
        match=f"Provided address {hex(0x111)} is different than computed address {hex(address)}",
    ):
        await Account.deploy_account_v3(
            address=0x111,
            class_hash=class_hash,
            salt=salt,
            key_pair=key_pair,
            client=client,
            resource_bounds=MAX_RESOURCE_BOUNDS,
        )


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1560)")
async def test_deploy_account_raises_on_no_enough_funds(
    deploy_account_details_factory, client
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    with patch(
        f"{FullNodeClient.__module__}.FullNodeClient.call_contract", AsyncMock()
    ) as mocked_balance:
        mocked_balance.return_value = (0, 0)

        with pytest.raises(
            ValueError,
            match="Not enough tokens at the specified address to cover deployment costs",
        ):
            await Account.deploy_account_v3(
                address=address,
                class_hash=class_hash,
                salt=salt,
                key_pair=key_pair,
                client=client,
                resource_bounds=MAX_RESOURCE_BOUNDS,
            )


@pytest.mark.asyncio
async def test_deploy_account_passes_on_enough_funds(
    deploy_account_details_factory, client
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    with patch(
        f"{FullNodeClient.__module__}.FullNodeClient.call_contract", AsyncMock()
    ) as mocked_balance, patch(
        f"{FullNodeClient.__module__}.FullNodeClient.deploy_account", AsyncMock()
    ) as mocked_deploy:
        mocked_balance.return_value = (0, 100)
        mocked_deploy.return_value = DeployAccountTransactionResponse(
            transaction_hash=0x1
        )

        await Account.deploy_account_v3(
            address=address,
            class_hash=class_hash,
            salt=salt,
            key_pair=key_pair,
            client=client,
            resource_bounds=MAX_RESOURCE_BOUNDS,
        )


# TODO (#1056): change this test to braavos account
@pytest.mark.skip(
    reason="'__validate_execute__' doesn't allow any other calldata than in the constructor"
)
@pytest.mark.asyncio
async def test_deploy_account_uses_custom_calldata(
    client, deploy_account_details_factory, fee_contract
):
    _, key_pair, salt, class_hash = await deploy_account_details_factory.get()
    calldata = [1, 2, 3, 4]
    address = compute_address(
        salt=salt,
        class_hash=class_hash,
        constructor_calldata=calldata,
        deployer_address=0,
    )

    res = await fee_contract.functions["transfer"].invoke(
        recipient=address, amount=int(1e16), resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await res.wait_for_acceptance()

    deploy_result = await Account.deploy_account_v3(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        constructor_calldata=calldata,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    tx = await client.get_transaction(deploy_result.hash)
    assert isinstance(tx, DeployAccountTransactionV3)
    assert tx.constructor_calldata == calldata


@pytest.mark.asyncio
async def test_sign_invoke_v3_for_fee_estimation(account, map_contract):
    call = map_contract.functions["put"].prepare_invoke_v3(key=1, value=2)
    transaction = await account.sign_invoke_v3(
        calls=call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    estimate_fee_transaction = await account.sign_for_fee_estimate(transaction)
    assert estimate_fee_transaction.version == transaction.version + 2**128

    estimation = await account.client.estimate_fee(estimate_fee_transaction)
    assert isinstance(estimation, EstimatedFee)
    assert estimation.unit == PriceUnit.FRI
    assert estimation.overall_fee > 0


@pytest.mark.asyncio
async def test_sign_transaction_custom_nonce(account, hello_starknet_class_hash):
    deployment = Deployer().create_contract_deployment(hello_starknet_class_hash)
    deploy_tx = await account.sign_invoke_v3(
        deployment.call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    new_balance = 30
    invoke_tx = await account.sign_invoke_v3(
        Call(
            deployment.address,
            get_selector_from_name("increase_balance"),
            [new_balance],
        ),
        nonce=deploy_tx.nonce + 1,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    deploy_res = await account.client.send_transaction(deploy_tx)
    invoke_res = await account.client.send_transaction(invoke_tx)

    await account.client.wait_for_tx(deploy_res.transaction_hash)
    await account.client.wait_for_tx(invoke_res.transaction_hash)

    result = await account.client.call_contract(
        Call(deployment.address, get_selector_from_name("get_balance"), [])
    )

    assert invoke_tx.nonce == deploy_tx.nonce + 1
    assert result == [new_balance]


@pytest.mark.asyncio
async def test_argent_account_deploy(
    client,
    argent_account_v040_data: AccountPrerequisites,
):
    deploy_result = await Account.deploy_account_v3(
        address=argent_account_v040_data.address,
        class_hash=ARGENT_V040_CLASS_HASH,
        salt=argent_account_v040_data.salt,
        key_pair=argent_account_v040_data.key_pair,
        client=client,
        constructor_calldata=argent_account_v040_data.calldata,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    await deploy_result.wait_for_acceptance()
    account = deploy_result.account

    assert isinstance(account, BaseAccount)
    assert await account.cairo_version == 1

    account_contract_class = await client.get_class_at(
        contract_address=account.address, block_number="latest"
    )

    assert isinstance(account_contract_class, SierraContractClass)


@pytest.mark.asyncio
async def test_argent_account_execute(
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    # verify that initial balance is 0
    get_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("get_balance"),
        calldata=[],
    )
    get_balance = await argent_account_v040.client.call_contract(
        call=get_balance_call, block_number="latest"
    )

    assert get_balance[0] == 0

    value = 20
    increase_balance_by_20_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[value],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_by_20_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    receipt = await argent_account_v040.client.get_transaction_receipt(
        tx_hash=execute.transaction_hash
    )

    assert receipt.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2

    # verify that the previous call was executed
    get_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("get_balance"),
        calldata=[],
    )
    get_balance = await argent_account_v040.client.call_contract(
        call=get_balance_call, block_number="latest"
    )

    assert get_balance[0] == value


@pytest.mark.asyncio
async def test_account_execute_v3(account, deployed_balance_contract):
    get_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("get_balance"),
        calldata=[],
    )
    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )

    (initial_balance,) = await account.client.call_contract(call=get_balance_call)

    execute_increase_balance = await account.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    receipt = await account.client.wait_for_tx(
        tx_hash=execute_increase_balance.transaction_hash
    )

    assert receipt.execution_status == TransactionExecutionStatus.SUCCEEDED

    tx_details = await account.client.get_transaction(
        tx_hash=execute_increase_balance.transaction_hash
    )
    assert isinstance(tx_details, InvokeTransactionV3)

    (balance_after_increase,) = await account.client.call_contract(
        call=get_balance_call
    )
    assert initial_balance + 100 == balance_after_increase


@pytest.mark.asyncio
async def test_invoke_v3_with_tip(account, hello_starknet_class_hash):
    deployment = Deployer().create_contract_deployment(hello_starknet_class_hash)

    invoke_tx = await account.execute_v3(
        Call(
            deployment.address,
            get_selector_from_name("increase_balance"),
            [20000],
        ),
        resource_bounds=MAX_RESOURCE_BOUNDS,
        tip=123456,
    )

    transaction = await account.client.get_transaction(
        tx_hash=invoke_tx.transaction_hash
    )

    assert isinstance(transaction, InvokeTransactionV3)
    assert transaction.tip == 123456


@pytest.mark.asyncio
async def test_deploy_account_v3_with_tip(client, deploy_account_details_factory):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    tip = 12345
    deploy_result = await Account.deploy_account_v3(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        resource_bounds=MAX_RESOURCE_BOUNDS,
        tip=tip,
    )
    await deploy_result.wait_for_acceptance()

    transaction = await client.get_transaction(tx_hash=deploy_result.hash)
    assert isinstance(transaction, DeployAccountTransactionV3)
    assert transaction.tip == tip


@pytest.mark.asyncio
async def test_declare_v3_with_tip(
    account, sierra_minimal_compiled_contract_and_class_hash
):
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash
    tip = 12345
    signed_tx = await account.sign_declare_v3(
        compiled_contract,
        compiled_class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
        tip=tip,
    )

    result = await account.client.declare(signed_tx)
    transaction = await account.client.get_transaction(tx_hash=result.transaction_hash)
    assert isinstance(transaction, DeclareTransactionV3)
    assert transaction.tip == tip
