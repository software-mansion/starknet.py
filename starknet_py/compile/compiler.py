import json
import os
import typing
import warnings
from pathlib import Path
from typing import List, Optional, Tuple, Union

from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import get_module_reader
from starkware.cairo.lang.compiler.constants import LIBS_DIR_ENVVAR, MAIN_SCOPE
from starkware.cairo.lang.compiler.preprocessor.preprocess_codes import preprocess_codes
from starkware.starknet.compiler.compile import (
    StarknetPreprocessedProgram,
    assemble_starknet_contract,
)
from starkware.starknet.compiler.starknet_pass_manager import starknet_pass_manager

from starknet_py.net.client_models import ContractClass
from starknet_py.net.schemas.gateway import ContractClassSchema

CairoSourceCode = str
CairoFilename = str
StarknetCompilationSource = Union[CairoSourceCode, List[CairoFilename]]


class Compiler:
    """
    Class for compiling Cairo contracts
    """

    def __init__(
        self,
        contract_source: StarknetCompilationSource,
        is_account_contract: bool = False,
        cairo_path: Optional[List[str]] = None,
    ):
        """
        Initializes compiler.

        :param contract_source: a list of source files paths
        :param is_account_contract: Set this to ``True`` to compile account contracts
        :param cairo_path: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
        """
        warnings.warn(
            "Compiler module is deprecated and will be removed in the future. "
            "Consider compiling contracts using other tools.",
            category=DeprecationWarning,
        )
        self.contract_source = contract_source
        self.is_account_contract = is_account_contract
        self.search_paths = cairo_path

    def compile_contract(self) -> str:
        """
        Compiles a contract and returns it as string

        :raises PreprocessorError: when is_account_contract parameter is incorrectly set
        :return: string of compiled contract
        """
        return starknet_compile(
            source=self.contract_source,
            is_account_contract=self.is_account_contract,
            search_paths=self.search_paths,
        )


def create_contract_class(
    compiled_contract: str,
) -> ContractClass:
    """
    Creates ContractClass from already compiled contract.

    :return: a ContractClass instance.
    """
    return typing.cast(ContractClass, ContractClassSchema().loads(compiled_contract))


def load_cairo_source_code(filename: CairoFilename) -> str:
    source_file = Path(filename)

    if not source_file.is_file():
        raise ValueError(f"File {filename} does not exist.")

    if source_file.suffix != ".cairo":
        raise ValueError(f"File {filename} is not a cairo source file.")

    return Path(filename).read_text("utf-8")


def load_source_code(
    src: StarknetCompilationSource,
) -> List[Tuple[str, str]]:
    if isinstance(src, str):
        return [(src, str(hash(src)))]
    return [(load_cairo_source_code(filename), filename) for filename in src]


def starknet_compile(
    source: StarknetCompilationSource,
    is_account_contract: bool = False,
    search_paths: Optional[List[str]] = None,
):
    file_contents_for_debug_info = {}

    cairo_path: List[str] = list(
        filter(None, os.getenv(LIBS_DIR_ENVVAR, "").split(":"))
    )

    if search_paths is not None:
        cairo_path += search_paths

    module_reader = get_module_reader(cairo_path=cairo_path)

    pass_manager = starknet_pass_manager(
        prime=DEFAULT_PRIME,
        read_module=module_reader.read,
        disable_hint_validation=True,
    )

    preprocessed = preprocess_codes(
        codes=load_source_code(source),
        pass_manager=pass_manager,
        main_scope=MAIN_SCOPE,
    )
    preprocessed = typing.cast(StarknetPreprocessedProgram, preprocessed)

    assembled_program = assemble_starknet_contract(
        preprocessed,
        main_scope=MAIN_SCOPE,
        add_debug_info=False,
        file_contents_for_debug_info=file_contents_for_debug_info,
        filter_identifiers=True,
        is_account_contract=is_account_contract,
    )

    return json.dumps(
        assembled_program.Schema().dump(assembled_program),
        indent=4,
        sort_keys=True,
    )
