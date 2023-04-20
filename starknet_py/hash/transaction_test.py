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
    "contract_json, data, expected_declare_hash",
    (
        (
            "map_compiled.json",
            [3, 4, 5, 1, 7],
            0x6178AE10CF37D36CA25B63342BD8A96ACE651BA690A10160F4826B9965D9133,
        ),
        (
            "balance_compiled.json",
            [23, 24, 25, 26, 27],
            0x4F4666A11FE9479F0126B7FDC50BD37FA7AF65BE1B54D5151F985D1F96BF2E0,
        ),
    ),
)
def test_compute_declare_transaction_hash(contract_json, data, expected_declare_hash):
    contract = read_contract(contract_json)
    compiled_contract = create_compiled_contract(compiled_contract=contract)

    declare_hash = compute_declare_transaction_hash(compiled_contract, *data)

    assert declare_hash == expected_declare_hash


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_declare_v2_hash",
    (
        (
            "account_compiled",
            0x23ADCD880276B0F56ADD013F22B2DE47F128A42496F6244BC7A276C93B62215,
        ),
        (
            "erc20_compiled",
            0x16D944106C3FF0A7999D267C17C8227483A5EA750CCFA6E2956AE64FB1E1666,
        ),
        (
            "minimal_contract_compiled",
            0x5B85A51C7A7190B7AFD755B03AE32AE30D597BC943DBA4453F1E53AE3F65D87,
        ),
    ),
)
def test_compute_declare_v2_transaction_hash(
    sierra_contract_class_source, expected_declare_v2_hash
):
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

    assert declare_v2_hash == expected_declare_v2_hash
