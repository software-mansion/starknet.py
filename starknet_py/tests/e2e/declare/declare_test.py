import pytest

from starknet_py.net.client_models import TransactionExecutionStatus
from starknet_py.net.models.transaction import DeclareV3
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_declare_v3_tx(account, abi_types_compiled_contract_and_class_hash):
    declare_tx = await account.sign_declare_v3(
        compiled_contract=abi_types_compiled_contract_and_class_hash[0],
        compiled_class_hash=abi_types_compiled_contract_and_class_hash[1],
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    assert isinstance(declare_tx, DeclareV3)

    result = await account.client.declare(declare_tx)
    tx_receipt = await account.client.wait_for_tx(tx_hash=result.transaction_hash)

    assert tx_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED
