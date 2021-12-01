import os

from src.utils.compiler.starknet_compile import starknet_compile, CairoSourceFile
from src.utils.files import file_from_directory

directory = os.path.dirname(__file__)


def test_starknet_compilation():
    test_filename = file_from_directory(directory, "map.cairo")
    test_file_content = open(test_filename).read()

    output_file_str = starknet_compile(
        [CairoSourceFile(content=test_file_content, name=test_filename)]
    )
    assert output_file_str is not None  # TODO: Make this better
