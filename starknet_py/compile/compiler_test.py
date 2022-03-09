import json
from starkware.starknet.services.api.contract_definition import ContractDefinition

from starknet_py.compile.compiler import Compiler
from starknet_py.compile.map import MAP_CONTRACT
from starknet_py.compile.map_compiled import MAP_COMPILED


def test_compile():
    output_file_str = Compiler.compile_contract(MAP_CONTRACT)
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_create_definition_from_source():
    contract = Compiler.create_contract_definition(contract_source=MAP_CONTRACT)

    assert isinstance(contract, ContractDefinition)


def test_create_definition_from_compiled():
    contract = Compiler.create_contract_definition(compiled_contract=MAP_COMPILED)

    assert isinstance(contract, ContractDefinition)
