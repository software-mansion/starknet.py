from typing import Optional

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash


def _extract_compiled_class_hash(
    compiled_contract_casm: Optional[str] = None,
    compiled_class_hash: Optional[int] = None,
) -> int:
    if compiled_class_hash is None and compiled_contract_casm is None:
        raise ValueError(
            "For Cairo 1.0 contracts, either the 'compiled_class_hash' or the 'compiled_contract_casm' "
            "argument must be provided."
        )

    if compiled_class_hash is None:
        assert compiled_contract_casm is not None
        compiled_class_hash = compute_casm_class_hash(
            create_casm_class(compiled_contract_casm)
        )

    return compiled_class_hash
