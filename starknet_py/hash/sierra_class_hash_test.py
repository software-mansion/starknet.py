import json
from typing import cast

import pytest

from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.net.client_models import SierraContractClass
from starknet_py.net.schemas.gateway import SierraContractClassSchema
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("minimal_contract_compiled.json", 0x38914973FCAB1F5DDC803CB31304EA9A7849E97023805DA6FFB9F4DDFBCDF8B),
        ("hello_starknet_compiled.json", 0x345DF0A9B35CE05D03772BA7938ACAD66921C5C39C1A5AF74AEE72AA25C363E),
        ("erc20_compiled.json", 0x4BC5ED5186C60E91B8A8F0D8CDAB4A4D4865D8991B6617274BE7728A7F658B4),
        ("account_compiled.json", 0x63805CDB9F8A5CA46AC82EA910A7D2F316C11006E82DC770A3235883A7645B1),
        ("test_contract_compiled.json", 0x455ED420BEE4E2B9275802CE444B7B57666E64A52BF062A2CE504CA34FCA0F4),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )
    sierra_contract_class_dict = json.loads(sierra_contract_class_str)
    sierra_contract_class_dict["abi"] = json.dumps(sierra_contract_class_dict["abi"])
    del sierra_contract_class_dict["sierra_program_debug_info"]

    sierra_contract_class = cast(
        SierraContractClass,
        SierraContractClassSchema().load(sierra_contract_class_dict),
    )
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
