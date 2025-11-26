import importlib.util
import os
import sys

import pytest


def _import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


def assert_no_circular_imports(package_name: str):
    for path, _, files in os.walk(package_name):
        py_files = [f for f in files if f.endswith(".py")]
        for file in py_files:
            file_path = os.path.join(path, file)
            relative_path = os.path.relpath(file_path, package_name)
            module_path_no_ext = relative_path.removesuffix(".py")

            # Handle __init__.py files specially
            if module_path_no_ext.endswith("__init__"):
                module_path_no_init = module_path_no_ext.removesuffix(
                    "__init__"
                ).rstrip(os.sep)

                # Top-level __init__.py gives empty module path
                if not module_path_no_init:
                    module_name = package_name
                else:
                    dotted_module_path = module_path_no_init.replace(os.sep, ".")
                    module_name = f"{package_name}.{dotted_module_path}"
            else:
                dotted_module_path = module_path_no_ext.replace(os.sep, ".")
                module_name = f"{package_name}.{dotted_module_path}"

            _import_from_path(module_name, file_path)


def test_circular_imports_absent():
    assert_no_circular_imports("starknet_py")


def test_circular_imports_present():
    package_name = "circular_import_mocks"

    error_regex = (
        rf"(?:"
        rf"cannot import name 'A' from '{package_name}.file_a' \(.*{package_name}[\\/]+file_a\.py\)"
        rf"|"
        rf"cannot import name 'B' from '{package_name}.file_b' \(.*{package_name}[\\/]+file_b\.py\)"
        rf")"
    )
    with pytest.raises(ImportError, match=error_regex):
        assert_no_circular_imports(package_name)
