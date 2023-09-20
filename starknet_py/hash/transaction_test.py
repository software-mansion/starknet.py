import pytest

from starknet_py.common import create_compiled_contract
from starknet_py.hash.transaction import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_declare_v2_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_invoke_transaction_hash,
    compute_transaction_hash,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V0_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            [TransactionHashPrefix.INVOKE, 2, 3, 4, [5], 6, 7, [8]],
            1176541524183318710439453346174486593835028723304878846501762065493748312757,
        ),
        (
            [TransactionHashPrefix.L1_HANDLER, 15, 39, 74, [74], 39, 15, [28]],
            1226653506056503634668815848352741482067480791322607584496401451909331743178,
        ),
        (
            [
                TransactionHashPrefix.INVOKE,
                0x0,
                0x2A,
                0x64,
                [],
                0x0,
                StarknetChainId.TESTNET,
            ],
            0x7D260744DE9D8C55E7675A34512D1951A7B262C79E685D26599EDD2948DE959,
        ),
    ),
)
def test_compute_transaction_hash(data, expected_hash):
    assert compute_transaction_hash(*data) == expected_hash


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            {
                "contract_address": 2,
                "class_hash": 3,
                "constructor_calldata": [4],
                "salt": 5,
                "version": 6,
                "max_fee": 7,
                "chain_id": 8,
                "nonce": 9,
            },
            0x6199E956E541CBB06589C4A63C2578A8ED6B697C0FA35B002F48923DFE648EE,
        ),
    ),
)
def test_compute_deploy_account_transaction_hash(data, expected_hash):
    assert compute_deploy_account_transaction_hash(**data) == expected_hash


@pytest.mark.parametrize(
    "contract_json, data",
    [
        ("map_compiled.json", [3, 4, 5, 1, 7]),
        ("balance_compiled.json", [23, 24, 25, 26, 27]),
    ],
)
def test_compute_declare_transaction_hash(contract_json, data):
    contract = read_contract(contract_json, directory=CONTRACTS_COMPILED_V0_DIR)
    compiled_contract = create_compiled_contract(compiled_contract=contract)

    declare_hash = compute_declare_transaction_hash(compiled_contract, *data)

    assert declare_hash > 0


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            {
                "class_hash": 2,
                "sender_address": 3,
                "version": 4,
                "max_fee": 5,
                "chain_id": 6,
                "nonce": 7,
                "compiled_class_hash": 8,
            },
            0x67EA411072DD2EF3BA36D9680F040A02E599F80F4770E204ECBB2C47C226793,
        ),
    ),
)
def test_compute_declare_v2_transaction_hash(data, expected_hash):
    assert compute_declare_v2_transaction_hash(**data) == expected_hash


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            {
                "sender_address": 3,
                "version": 4,
                "calldata": [5],
                "max_fee": 6,
                "chain_id": 7,
                "nonce": 8,
            },
            0x505BBF7CD810531C53526631078DAA314BFD036C80C7C6E3A02C608DB8E31DE,
        ),
    ),
)
def test_compute_invoke_transaction_hash(data, expected_hash):
    assert compute_invoke_transaction_hash(**data) == expected_hash
