import json
import os
from pathlib import Path

import pytest
from starkware.cairo.lang.compiler.constants import LIBS_DIR_ENVVAR
from starkware.cairo.lang.compiler.import_loader import ImportLoaderError
from starkware.starknet.services.api.contract_definition import ContractDefinition

from starknet_py.compile.compiler import Compiler

directory = os.path.dirname(__file__)

test_file_path = Path(directory, "map.cairo")
test_file_content = test_file_path.read_text("utf-8")

mock_contracts_base_path = Path(directory, "mock-contracts")
base_contract_path = Path(os.path.join(mock_contracts_base_path, "base.cairo"))


def test_compile_direct_load():
    output_file_str = Compiler.compile_contract(test_file_content)
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_compile_file_load():
    output_file_str = Compiler.compile_contract([test_file_path.resolve().absolute()])
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_compile_throws_on_non_existing_file():
    with pytest.raises(TypeError) as t_err:
        Compiler.compile_contract(["nonexisting.cairo"])
    assert "does not exist" in str(t_err.value)


def test_throws_on_compile_with_wrong_extension():
    current_filename = f"{__name__.rsplit('.', maxsplit=1)[-1]}.py"
    full_current_file_pathname = str(Path(directory, current_filename))
    with pytest.raises(TypeError) as t_err:
        Compiler.compile_contract([full_current_file_pathname])
    assert "is not a cairo source file" in str(t_err.value)


def test_compile_with_search_path():
    output_file_str = Compiler.compile_contract(
        [base_contract_path.resolve().absolute()],
        search_paths=[mock_contracts_base_path],
    )
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_compile_with_env_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(LIBS_DIR_ENVVAR, str(mock_contracts_base_path))
    output_file_str = Compiler.compile_contract(
        [base_contract_path.resolve().absolute()]
    )
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_throws_on_compile_without_search_path_and_env_var():
    with pytest.raises(ImportLoaderError) as m_err:
        Compiler.compile_contract([base_contract_path.resolve().absolute()])
    assert "Could not find module 'inner.inner'." in str(m_err.value)


def test_create_definition_from_source():
    contract = Compiler.create_contract_definition(contract_source=test_file_content)

    assert isinstance(contract, ContractDefinition)


def test_create_definition_from_compiled():
    compiled_contract = Compiler.compile_contract(test_file_content)
    contract = Compiler.create_contract_definition(compiled_contract=compiled_contract)

    assert isinstance(contract, ContractDefinition)
