import json
import os
from pathlib import Path

from starknet_py.utils.compiler.starknet_compile import starknet_compile

directory = os.path.dirname(__file__)

test_file_content = Path(directory, "map.cairo").read_text("utf-8")


def test_starknet_compilation():
    output_file_str = starknet_compile({"map": test_file_content})
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []
