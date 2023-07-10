import json

import pytest

from starknet_py.abi.v2.model import Abi
from starknet_py.abi.v2.parser import AbiParser
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_name",
    [
        "abi_types",
        "account",
        "erc20",
        "hello2",
        "hello_starknet",
        "minimal_contract",
        "new_syntax_test_contract",
        "test_contract",
        "test_enum",
        "test_option",
        "token_bridge",
    ],
)
def test_abi_parse(contract_name):
    abi = json.loads(
        read_contract(
            f"{contract_name}_compiled.json", directory=CONTRACTS_COMPILED_V2_DIR
        )
    )["abi"]

    parser = AbiParser(abi)
    parsed_abi = parser.parse()

    assert isinstance(parsed_abi, Abi)
