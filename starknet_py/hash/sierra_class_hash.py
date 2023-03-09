from typing import List

from starkware.cairo.common.poseidon_hash import poseidon_hash_many

from starknet_py.common import int_from_bytes
from starknet_py.hash.utils import _starknet_keccak
from starknet_py.net.client_models import NewContractClass, NewEntryPoint


def compute_sierra_class_hash(sierra_contract_class: NewContractClass) -> int:
    """
    Calculate class hash of a NewContractClass.
    """
    sierra_version = int_from_bytes(
        ("CONTRACT_CLASS_V" + sierra_contract_class.contract_class_version).encode(
            "ascii"
        )
    )

    _entry_points = sierra_contract_class.entry_points_by_type

    external_entry_points_hash = poseidon_hash_many(
        _entry_points_array(_entry_points.external)
    )
    l1_handler_entry_points_hash = poseidon_hash_many(
        _entry_points_array(_entry_points.l1_handler)
    )
    constructor_entry_points_hash = poseidon_hash_many(
        _entry_points_array(_entry_points.constructor)
    )

    assert sierra_contract_class.abi is not None
    abi_hash = _starknet_keccak(bytes(sierra_contract_class.abi, "utf-8"))

    _sierra_program = [int(val, 0) for val in sierra_contract_class.sierra_program]
    sierra_program_hash = poseidon_hash_many(_sierra_program)

    return poseidon_hash_many(
        [
            sierra_version,
            external_entry_points_hash,
            l1_handler_entry_points_hash,
            constructor_entry_points_hash,
            abi_hash,
            sierra_program_hash,
        ]
    )


def _entry_points_array(entry_points: List[NewEntryPoint]) -> List[int]:
    entry_points_array = []
    for entry_point in entry_points:
        entry_points_array.extend([entry_point.selector, entry_point.function_idx])

    return entry_points_array
