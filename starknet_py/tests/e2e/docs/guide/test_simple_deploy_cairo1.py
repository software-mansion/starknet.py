import json
import sys

import pytest

from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


# TODO (#1219): investigate why this test fails for v1 contract
@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Some cairo 1 contracts compiled with v1 compiler fail with new devnet-rs - test simply for a code example.",
)
@pytest.mark.asyncio
async def test_simple_deploy_cairo1(account, cairo1_erc20_class_hash):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.cairo.felt import encode_shortstring
    from starknet_py.common import create_sierra_compiled_contract
    from starknet_py.contract import Contract

    # docs: end

    compiled_contract = read_contract(
        "erc20_compiled.json", directory=CONTRACTS_COMPILED_V2_DIR
    )
    class_hash = cairo1_erc20_class_hash

    # docs: start
    abi = create_sierra_compiled_contract(compiled_contract=compiled_contract).abi

    constructor_args = {
        "name_": encode_shortstring("erc20_basic"),
        "symbol_": encode_shortstring("ERC20B"),
        "decimals_": 10,
        "initial_supply": 12345,
        "recipient": account.address,
    }

    deploy_result = await Contract.deploy_contract_v1(
        account=account,
        class_hash=class_hash,
        abi=json.loads(abi),
        constructor_args=constructor_args,
        max_fee=int(1e16),
        cairo_version=1,  # note the `cairo_version` parameter
    )

    await deploy_result.wait_for_acceptance()
    contract = deploy_result.deployed_contract
    # docs: end

    assert contract.address != 0
