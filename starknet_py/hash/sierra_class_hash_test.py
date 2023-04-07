import json
from typing import cast

import pytest

from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.net.client_models import SierraContractClass
from starknet_py.net.schemas.gateway import SierraContractClassSchema
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    [
        ("minimal_contract_compiled.json", 1599138706221378695920886452283598990366208146534789309105817346994670985099),
        ("hello_starknet_compiled.json", 1402049461193027466671798372365280774461718071718973217192904594674113331672),
        ("token_bridge_compiled.json", 1432532835947815742986859328111556482030872495044723531555601367498744473873),
        ("erc20_compiled.json", 3412857632605585557918497147109067252175091479230565951878129401615980815133),
        ("account_compiled.json", 1086909747821093764020466308682800050191071334282982233544773177113331945129),
        ("test_contract_compiled.json", 1383912190427821093695301078411999332469349645429605971905505721182641007028)
    ],
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
