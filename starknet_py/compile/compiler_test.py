import json
import os
from pathlib import Path

import pytest
from starkware.cairo.lang.compiler.constants import LIBS_DIR_ENVVAR
from starkware.cairo.lang.compiler.import_loader import ImportLoaderError
from starkware.starknet.compiler.validation_utils import PreprocessorError
from starkware.starknet.services.api.contract_class import ContractClass

from starknet_py.compile.compiler import Compiler, create_contract_class
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_DIR

directory = os.path.dirname(__file__)

test_file_path = CONTRACTS_DIR / "map.cairo"
test_file_content = test_file_path.read_text("utf-8")

base_contract_path = CONTRACTS_DIR / "base.cairo"

mock_account_path = CONTRACTS_DIR / "mock_account.cairo"
mock_account_content = mock_account_path.read_text("utf-8")


def test_compile_direct_load():
    output_file_str = Compiler(contract_source=test_file_content).compile_contract()
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_compile_file_load():
    output_file_str = Compiler(
        contract_source=[str(test_file_path.resolve().absolute())]
    ).compile_contract()
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_compile_throws_on_non_existing_file():
    with pytest.raises(ValueError, match="does not exist"):
        Compiler(contract_source=["nonexisting.cairo"]).compile_contract()


def test_throws_on_compile_with_wrong_extension():
    current_filename = f"{__name__.rsplit('.', maxsplit=1)[-1]}.py"
    full_current_file_pathname = str(Path(directory, current_filename))
    with pytest.raises(ValueError, match="is not a cairo source file"):
        Compiler(contract_source=[full_current_file_pathname]).compile_contract()


def test_compile_with_search_path():
    output_file_str = Compiler(
        contract_source=[str(base_contract_path.resolve().absolute())],
        cairo_path=[str(CONTRACTS_DIR)],
    ).compile_contract()
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_compile_with_env_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(LIBS_DIR_ENVVAR, str(CONTRACTS_DIR))
    output_file_str = Compiler(
        contract_source=[str(base_contract_path.resolve().absolute())]
    ).compile_contract()
    output_json = json.loads(output_file_str)

    assert output_json.get("abi") != []


def test_throws_on_compile_without_search_path_and_env_var():
    with pytest.raises(ImportLoaderError, match="Could not find module 'inner.inner'."):
        Compiler(
            contract_source=[str(base_contract_path.resolve().absolute())]
        ).compile_contract()


def test_create_definition():
    compiled = Compiler(contract_source=test_file_content).compile_contract()
    contract = create_contract_class(compiled)

    assert isinstance(contract, ContractClass)


def test_compile_account_contract():
    output = Compiler(
        contract_source=mock_account_content, is_account_contract=True
    ).compile_contract()
    output_json = json.loads(output)

    assert output_json.get("abi") != []


def test_compile_account_contract_throws_without_is_account_contract():
    with pytest.raises(PreprocessorError):
        Compiler(contract_source=mock_account_content).compile_contract()


def test_compile_standard_contract_throws_with_is_account_contract():
    with pytest.raises(PreprocessorError):
        Compiler(
            contract_source=test_file_content, is_account_contract=True
        ).compile_contract()
