from typing import Optional, List, Union, Literal

from starkware.starknet.services.api.contract_class import ContractClass

from starknet_py.compile.compiler import (
    StarknetCompilationSource,
    Compiler,
    create_contract_class,
)


def create_compiled_contract(
    compilation_source: Optional[StarknetCompilationSource] = None,
    compiled_contract: Optional[str] = None,
    search_paths: Optional[List[str]] = None,
) -> ContractClass:
    if not compiled_contract:
        if not compilation_source:
            raise ValueError(
                "One of compiled_contract or compilation_source is required."
            )

        compiled_contract = Compiler(
            contract_source=compilation_source, cairo_path=search_paths
        ).compile_contract()
    definition = create_contract_class(compiled_contract)
    return definition


def int_from_hex(number: Union[str, int]) -> int:
    return number if isinstance(number, int) else int(number, 16)


def int_from_bytes(
    value: bytes,
    byte_order: Literal["big", "little"] = "big",
    signed: bool = False,
) -> int:
    """
    Converts the given bytes object (parsed according to the given byte order) to an integer.
    """
    return int.from_bytes(value, byteorder=byte_order, signed=signed)
