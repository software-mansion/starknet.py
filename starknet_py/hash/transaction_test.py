import pytest

from starknet_py.common import (
    create_casm_class,
    create_compiled_contract,
    create_sierra_compiled_contract,
)
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.hash.transaction import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_declare_v2_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_transaction_hash,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "data, calculated_hash",
    (
        (
            [TransactionHashPrefix.INVOKE, 2, 3, 4, [5], 6, 7, [8]],
            1176541524183318710439453346174486593835028723304878846501762065493748312757,
        ),
        (
            [TransactionHashPrefix.L1_HANDLER, 15, 39, 74, [74], 39, 15, [28]],
            1226653506056503634668815848352741482067480791322607584496401451909331743178,
        ),
    ),
)
def test_compute_transaction_hash(data, calculated_hash):
    assert compute_transaction_hash(*data) == calculated_hash


@pytest.mark.parametrize(
    "data, calculated_hash",
    (
        (
            [2, 3, 4, [5], 6, 7, 8, 9],
            3319639522829811634906602140344071246050815451799261765214603967516640029516,
        ),
        (
            [12, 23, 34, [45], 56, 67, 78, 89],
            1704331554042454954615983716430494560849200211800542196314933915246556687567,
        ),
    ),
)
def test_compute_deploy_account_transaction_hash(data, calculated_hash):
    assert compute_deploy_account_transaction_hash(*data) == calculated_hash


@pytest.mark.parametrize(
    "contract_json, data",
    [
        ("map_compiled.json", [3, 4, 5, 1, 7]),
        ("balance_compiled.json", [23, 24, 25, 26, 27]),
    ],
)
def test_compute_declare_transaction_hash(contract_json, data):
    contract = read_contract(contract_json)
    compiled_contract = create_compiled_contract(compiled_contract=contract)

    declare_hash = compute_declare_transaction_hash(compiled_contract, *data)

    assert declare_hash > 0


@pytest.mark.parametrize(
    "sierra_contract_class_source",
    ["account_compiled", "erc20_compiled", "minimal_contract_compiled"],
)
def test_compute_declare_v2_transaction_hash(sierra_contract_class_source):
    compiled_contract = read_contract(
        f"{sierra_contract_class_source}.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_contract_casm = read_contract(
        f"{sierra_contract_class_source}.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )
    casm_class = create_casm_class(compiled_contract_casm)
    casm_class_hash = compute_casm_class_hash(casm_class)

    compiled_contract = create_sierra_compiled_contract(compiled_contract)

    declare_v2_hash = compute_declare_v2_transaction_hash(
        contract_class=compiled_contract,
        compiled_class_hash=casm_class_hash,
        chain_id=StarknetChainId.TESTNET.value,
        sender_address=0x1,
        max_fee=2000,
        version=2,
        nonce=23,
    )

    assert declare_v2_hash > 0
