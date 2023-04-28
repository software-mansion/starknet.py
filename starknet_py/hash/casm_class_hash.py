from typing import List

from poseidon_py.poseidon_hash import poseidon_hash_many

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.net.client_models import CasmClass, CasmClassEntryPoint

CASM_CLASS_VERSION = "COMPILED_CLASS_V1"


def compute_casm_class_hash(casm_contract_class: CasmClass) -> int:
    """
    Calculate class hash of a CasmClass.
    """
    casm_class_version = encode_shortstring(CASM_CLASS_VERSION)

    _entry_points = casm_contract_class.entry_points_by_type

    external_entry_points_hash = poseidon_hash_many(
        _entry_points_array(_entry_points.external)
    )
    l1_handler_entry_points_hash = poseidon_hash_many(
        _entry_points_array(_entry_points.l1_handler)
    )
    constructor_entry_points_hash = poseidon_hash_many(
        _entry_points_array(_entry_points.constructor)
    )

    bytecode_hash = poseidon_hash_many(casm_contract_class.bytecode)

    return poseidon_hash_many(
        [
            casm_class_version,
            external_entry_points_hash,
            l1_handler_entry_points_hash,
            constructor_entry_points_hash,
            bytecode_hash,
        ]
    )


def _entry_points_array(entry_points: List[CasmClassEntryPoint]) -> List[int]:
    entry_points_array = []
    for entry_point in entry_points:
        assert entry_point.builtins is not None
        _encoded_builtins = [encode_shortstring(val) for val in entry_point.builtins]
        builtins_hash = poseidon_hash_many(_encoded_builtins)

        entry_points_array.extend(
            [entry_point.selector, entry_point.offset, builtins_hash]
        )

    return entry_points_array
