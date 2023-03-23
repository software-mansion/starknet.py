import warnings
from typing import List, Literal, Optional, Union, cast

from marshmallow import EXCLUDE

from starknet_py.compile.compiler import Compiler, StarknetCompilationSource
from starknet_py.net.client_models import (
    CompiledContract,
    ContractClass,
    SierraCompiledContract,
)
from starknet_py.net.schemas.gateway import (
    CompiledContractSchema,
    ContractClassSchema,
    SierraCompiledContractSchema,
)


def create_compiled_contract(
    compilation_source: Optional[StarknetCompilationSource] = None,
    compiled_contract: Optional[str] = None,
    search_paths: Optional[List[str]] = None,
) -> CompiledContract:
    """
    Creates CompiledContract instance.

    :param compilation_source:
        source of the contract to be compiled.

         .. deprecated:: 0.15.0
            Argument compilation_source has been deprecated. Use compiled_contract instead.
    :param compiled_contract: compiled contract string.
    :param search_paths:
        paths used to resolve compilation dependencies.

         .. deprecated:: 0.15.0
            Argument search_paths has been deprecated. Use compiled_contract instead.
    :return: CompiledContract instance.
    """
    warnings.warn(
        "Argument compilation_source is deprecated and will be removed in the future. "
        "Consider using already compiled contracts instead.",
        category=DeprecationWarning,
    )

    if not compiled_contract:
        if not compilation_source:
            raise ValueError(
                "One of compiled_contract or compilation_source is required."
            )

        compiled_contract = Compiler(
            contract_source=compilation_source, cairo_path=search_paths
        ).compile_contract()
    return cast(CompiledContract, CompiledContractSchema().loads(compiled_contract))


def create_sierra_compiled_contract(compiled_contract: str) -> SierraCompiledContract:
    """
    Creates SierraCompiledContract instance.

    :param compiled_contract: compiled contract string.
    :return: SierraCompiledContract instance.
    """
    return cast(
        SierraCompiledContract,
        SierraCompiledContractSchema().loads(compiled_contract, unknown=EXCLUDE),
    )


def create_contract_class(
    compiled_contract: str,
) -> ContractClass:
    """
    Creates ContractClass from already compiled contract.

     .. deprecated:: 0.15.0
        Function create_contract_class is deprecated and will be removed in the future.
        Use :meth:`create_compiled_contract` instead.

    :return: a ContractClass.
    """
    warnings.warn(
        "Function create_contract_class is deprecated and will be removed in the future. "
        "Consider using create_compiled_contract instead.",
        category=DeprecationWarning,
    )
    return cast(ContractClass, ContractClassSchema().loads(compiled_contract))


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
