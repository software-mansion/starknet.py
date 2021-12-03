import json
import os

from starknet.utils.compiler.starknet_compile import starknet_compile

directory = os.path.dirname(__file__)

map_filename = os.path.join(directory, "map.cairo")
test_file_content = open(map_filename).read()


def test_starknet_compilation():
    output_file_str = starknet_compile({map_filename: test_file_content})
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []
