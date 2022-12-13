from typing import Optional, List, Union, Literal

from eth_utils.crypto import keccak
from starkware.cairo.lang.vm.crypto import pedersen_hash
from starkware.starknet.services.api.contract_class import ContractClass

from starknet_py.compile.compiler import (
    StarknetCompilationSource,
    Compiler,
    create_contract_class,
)
from starknet_py.constants import (
    DEFAULT_ENTRY_POINT_SELECTOR,
    DEFAULT_L1_ENTRY_POINT_NAME,
    DEFAULT_ENTRY_POINT_NAME,
    ADDR_BOUND,
    MASK_250,
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


def get_selector_from_name(func_name: str) -> int:
    """
    Returns the selector of a contract's function name.
    """
    if func_name in [DEFAULT_ENTRY_POINT_NAME, DEFAULT_L1_ENTRY_POINT_NAME]:
        return DEFAULT_ENTRY_POINT_SELECTOR

    return starknet_keccak(data=func_name.encode("ascii"))


def starknet_keccak(data: bytes) -> int:
    """
    A variant of eth-keccak that computes a value that fits in a StarkNet field element.
    """
    return int_from_bytes(keccak(data)) & MASK_250


def int_from_bytes(
    value: bytes,
    byte_order: Literal["big", "little"] = "big",
    signed: bool = False,
) -> int:
    """
    Converts the given bytes object (parsed according to the given byte order) to an integer.
    """
    return int.from_bytes(value, byteorder=byte_order, signed=signed)


def get_storage_var_address(var_name: str, *args) -> int:
    """
    Returns the storage address of a StarkNet storage variable given its name and arguments.
    """
    res = starknet_keccak(var_name.encode("ascii"))

    for arg in args:
        if not isinstance(arg, int):
            raise TypeError(f"Expected arguments to be integers. Found: {arg}.")
        res = pedersen_hash(res, arg)

    return res % ADDR_BOUND
