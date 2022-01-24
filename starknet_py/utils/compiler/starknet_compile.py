import json
import os
from pathlib import Path
from typing import List, Tuple, Union, NewType

from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import (
    get_module_reader,
)
from starkware.cairo.lang.compiler.constants import MAIN_SCOPE, LIBS_DIR_ENVVAR
from starkware.cairo.lang.compiler.preprocessor.preprocess_codes import preprocess_codes
from starkware.starknet.compiler.compile import assemble_starknet_contract
from starkware.starknet.compiler.starknet_pass_manager import starknet_pass_manager

CairoSourceCode = NewType("CairoSourceCode", str)
CairoFilename = NewType("CairoFilename", str)
StarknetCompilationSource = NewType(
    "CairoSource", Union[CairoSourceCode, List[CairoFilename]]
)


def load_cairo_source_code(filename: CairoFilename) -> str:
    source_file = Path(filename)

    if not source_file.is_file():
        raise TypeError(f"{filename} does not exist")

    if source_file.suffix != ".cairo":
        raise TypeError(f"{filename} is not a cairo source file")

    return Path(filename).read_text("utf-8")


def load_source_code(src: StarknetCompilationSource) -> List[Tuple[str, str]]:
    if isinstance(src, str):
        return [(src, str(hash(src)))]
    return [(load_cairo_source_code(filename), filename) for filename in src]


def starknet_compile(source: StarknetCompilationSource):
    file_contents_for_debug_info = {}

    cairo_path: List[str] = list(
        filter(None, os.getenv(LIBS_DIR_ENVVAR, "").split(":"))
    )
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

    assembled_program = assemble_starknet_contract(
        preprocessed,
        main_scope=MAIN_SCOPE,
        add_debug_info=False,
        file_contents_for_debug_info=file_contents_for_debug_info,
    )

    return json.dumps(
        assembled_program.Schema().dump(assembled_program),
        indent=4,
        sort_keys=True,
    )
