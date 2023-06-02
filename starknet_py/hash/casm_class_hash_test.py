# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x2645C161601C2D406225B32954497ADA29BF14A19363BCD6071DF9F25EA0620),
        ("erc20_compiled.casm", 0x18F95714044FD5408D3BF812BCD249DDEC098AB3CD201B7916170CFBFA59E05),
        ("hello_starknet_compiled.casm", 0x2C895E2F0AED646E6DEC493287B9EAF4CADCE8983AD3D60164E15A7B1C35F54),
        ("minimal_contract_compiled.casm", 0x46F2882281342DEA7694207216F95D925BA08EF4BE0CFF5E81E9057F49EF3C2),
        ("test_contract_compiled.casm", 0x636E18EAA5730715FDF7A618C00CA03F6F18F324E22482FA97406F8A2336E0F),
        ("token_bridge_compiled.casm", 0x4AFFA0C3F2CD95C4DE6B94EE483912562C1F7C253D719BF1A6925C5F737BE5A),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == expected_casm_class_hash
