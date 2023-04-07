import json
from typing import cast

import pytest

from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.net.client_models import SierraContractClass
from starknet_py.net.schemas.gateway import SierraContractClassSchema
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("minimal_contract_compiled.json", 0x38914973FCAB1F5DDC803CB31304EA9A7849E97023805DA6FFB9F4DDFBCDF8B),
        ("hello_starknet_compiled.json", 0x3198828D9AA172F0A2EFE0496D6BFA7065C4E90A2F52C4B81336E5AD5DC41D8),
        ("token_bridge_compiled.json", 0x32AC8EC0FC494976E5AEB9ABE5B7853424E6AD43DA75D47539905EDCCCD2911),
        ("erc20_compiled.json", 0x78B9BE5390A2CA1090561CF30092D19B14534A02BC867DA966793442C3DE31D),
        ("account_compiled.json", 0x2672B4B37F63EBA2A6D875B0CBC46B329C8DBBEEAC3E60B87D19B4CEEBCCEA9),
        ("test_contract_compiled.json", 0x30F443C1663E4D57483B653D089D81E2BC50FC6F5AF7D3C44E29F26251929B4),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        "precompiled/" + sierra_contract_class_source
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
