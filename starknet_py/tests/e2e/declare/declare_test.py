import pytest

from starknet_py.net.client_models import (
    ResourceBounds,
    ResourceBoundsMapping,
    TransactionExecutionStatus,
)
from starknet_py.net.models.transaction import DeclareV3
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS_L1


@pytest.mark.asyncio
async def test_declare_v2_tx(minimal_contract_class_hash: int):
    assert isinstance(minimal_contract_class_hash, int)
    assert minimal_contract_class_hash != 0


@pytest.mark.asyncio
async def test_declare_v3_tx(account, abi_types_compiled_contract_and_class_hash):
    resource_bounds = ResourceBoundsMapping(
        l1_gas=MAX_RESOURCE_BOUNDS_L1,
        l2_gas=ResourceBounds.init_with_zeros(),
    )
    declare_tx = await account.sign_declare_v3(
        compiled_contract=abi_types_compiled_contract_and_class_hash[0],
        compiled_class_hash=abi_types_compiled_contract_and_class_hash[1],
        resource_bounds=resource_bounds,
    )
    assert isinstance(declare_tx, DeclareV3)

    result = await account.client.declare(declare_tx)
    tx_receipt = await account.client.wait_for_tx(tx_hash=result.transaction_hash)

    assert tx_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED
