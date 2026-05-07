import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.client_models import TransactionExecutionStatus
from starknet_py.net.models.transaction import DeclareV3
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.fixtures.misc import load_contract


@pytest.mark.asyncio
async def test_declare_v3_tx(account):
    contract = load_contract(contract_name="TestContract5", package="contracts_v2")
    declare_tx = await account.sign_declare_v3(
        compiled_contract=contract["sierra"],
        compiled_class_hash=compute_casm_class_hash(
            create_casm_class(contract["casm"])
        ),
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    assert isinstance(declare_tx, DeclareV3)

    result = await account.client.declare(declare_tx)
    tx_receipt = await account.client.wait_for_tx(tx_hash=result.transaction_hash)

    assert tx_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED
