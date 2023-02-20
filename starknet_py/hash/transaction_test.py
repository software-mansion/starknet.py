import pytest

from starknet_py.common import create_compiled_contract
from starknet_py.hash.transaction import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_transaction_hash,
)
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
    "contract_class, data, calculated_hash",
    (
        (
            create_compiled_contract(
                compiled_contract=read_contract("map_compiled.json")
            ),
            [3, 4, 5, 0, 7],
            3541774834156044173802833283101285248062762410120835876882604474241326048804,
        ),
        (
            create_compiled_contract(
                compiled_contract=read_contract("balance_compiled.json")
            ),
            [23, 24, 25, 26, 27],
            281026346736086813081534934628468903582853878088256162569718459969487373872,
        ),
    ),
)
def test_compute_declare_transaction_hash(contract_class, data, calculated_hash):
    assert compute_declare_transaction_hash(contract_class, *data) == calculated_hash
