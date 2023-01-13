import json
from typing import List

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.cairo.utils import _starknet_keccak
from starknet_py.constants import API_VERSION
from starknet_py.net.client_models import DeclaredContract, EntryPoint
from starknet_py.utils.crypto.facade import compute_hash_on_elements


def compute_class_hash(contract_class: DeclaredContract) -> int:
    """
    Calculate class hash of a declared contract.
    """
    api_version = API_VERSION

    _entry_points = contract_class.entry_points_by_type

    external_entry_points_hash = compute_hash_on_elements(
        _entry_points_array(_entry_points.external)
    )
    l1_handler_entry_points_hash = compute_hash_on_elements(
        _entry_points_array(_entry_points.l1_handler)
    )
    constructor_entry_points_hash = compute_hash_on_elements(
        _entry_points_array(_entry_points.constructor)
    )

    _encoded_builtins = [
        encode_shortstring(builtin) for builtin in contract_class.program["builtins"]
    ]
    builtins_hash = compute_hash_on_elements(_encoded_builtins)

    hinted_class_hash = _compute_hinted_class_hash(contract_class)

    program_data_hash = compute_hash_on_elements(
        [int(data_, 0) for data_ in contract_class.program["data"]]
    )

    return compute_hash_on_elements(
        [
            api_version,
            external_entry_points_hash,
            l1_handler_entry_points_hash,
            constructor_entry_points_hash,
            builtins_hash,
            hinted_class_hash,
            program_data_hash,
        ]
    )


def _entry_points_array(entry_points: List[EntryPoint]) -> List[int]:
    entry_points_array = []
    for entry_point in entry_points:
        entry_points_array.extend([entry_point.selector, entry_point.offset])

    return entry_points_array


def _compute_hinted_class_hash(contract_class: DeclaredContract) -> int:
    program = contract_class.program
    program["debug_info"] = None

    if "attributes" in program:
        program = _delete_attributes(program)

    # Compilers in version < 0.10.0 did not have "compiler_version" field
    if "compiler_version" not in program:
        # The syntax used "(a: felt)" instead of "(a : felt)"
        raise ValueError(
            "Argument contract_class was compiled with a compiler before version 0.10.0. "
            "Calculating it's class_hash is not supported."
        )

    class_ = dict(abi=contract_class.abi, program=program)
    serialized_contract_class = json.dumps(obj=class_)
    return _starknet_keccak(data=serialized_contract_class.encode())


def _delete_attributes(program) -> dict:
    if len(program["attributes"]) == 0:
        # Remove attributes field from raw dictionary, for hash backward compatibility of
        # contracts deployed prior to adding this feature.
        del program["attributes"]
    else:
        # Remove accessible_scopes and flow_tracking_data fields from raw dictionary, for hash
        # backward compatibility of contracts deployed prior to adding this feature.
        for attr in program["attributes"]:
            if "accessible_scopes" in attr and len(attr["accessible_scopes"]) == 0:
                del attr["accessible_scopes"]
            if "flow_tracking_data" in attr and attr["flow_tracking_data"] is None:
                del attr["flow_tracking_data"]
    return program
