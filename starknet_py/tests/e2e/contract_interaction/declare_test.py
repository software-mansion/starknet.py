import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test_throws_when_cairo1_without_compiled_contract_casm(gateway_account):
    compiled_contract = read_contract(
        "erc20_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )

    with pytest.raises(
        ValueError,
        match="Cairo 1.0 contract was provided without compiled_contract_casm argument.",
    ):
        await Contract.declare(
            gateway_account, compiled_contract=compiled_contract, max_fee=MAX_FEE
        )
