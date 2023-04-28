import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x391b07aef5b45f1aaa22664d4dbc57e13ddef949fb14153e8a4ad25c09c8843),
        ("erc20_compiled.json", 0x7800885df80457bebd6f4a2791875e6d4b0cc26363c68d918917d5bc1803632),
        ("hello_starknet_compiled.json", 0x19fe4ae699bbe7328498a64c8ee596cfe1559a6fd64a54a6b9361af8376e932),
        ("minimal_contract_compiled.json", 0xa4991f661ab0137cd6f56bb69bd3480abe7e9e1d876b24ca1db28ba2ab07b6),
        ("test_contract_compiled.json", 0x1f87410d728736bcccea129f75c674ac1d3ff4e7a82aed56b8c12a559994556),
        ("token_bridge_compiled.json", 0x74970f8609b9603d1b9094f33fdfbf1ceb5c959fc4397a6e8118c97e6529e4a),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )
    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
