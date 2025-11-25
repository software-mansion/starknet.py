import importlib.util
import os
import shutil
import sys

import pytest

PACKAGE_NAME = "starknet_py"


def _import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


def assert_no_circular_imports():
    for path, _, files in os.walk(PACKAGE_NAME):
        py_files = [f for f in files if f.endswith(".py")]
        for file in py_files:
            file_path = os.path.join(path, file)

            relative_path = os.path.relpath(file_path, PACKAGE_NAME)
            module_path_no_ext = relative_path.removesuffix(".py")
            # Handle __init__.py files specially
            if module_path_no_ext.endswith("__init__"):
                module_path_no_init = module_path_no_ext.removesuffix(
                    "__init__"
                ).rstrip(os.sep)
                if not module_path_no_init:  # Top-level __init__.py
                    module_name = PACKAGE_NAME
                else:
                    dotted_module_path = module_path_no_init.replace(os.sep, ".")
                    module_name = f"{PACKAGE_NAME}.{dotted_module_path}"
            else:
                dotted_module_path = module_path_no_ext.replace(os.sep, ".")
                module_name = f"{PACKAGE_NAME}.{dotted_module_path}"

            _import_from_path(module_name, file_path)


def test_circular_imports_absent():
    assert_no_circular_imports()


def _run_circular_import_test(module_name, import_a, import_b):
    module_path = os.path.join(PACKAGE_NAME, module_name)
    os.makedirs(module_path, exist_ok=True)
    try:
        with open(os.path.join(module_path, "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(module_path, "file_a.py"), "w") as f:
            f.write(f"{import_a}\nclass A:\n    pass\n")
        with open(os.path.join(module_path, "file_b.py"), "w") as f:
            f.write(f"{import_b}\nclass B:\n    pass\n")
        error_regex = (
            rf"cannot import name '[AB]' from '{PACKAGE_NAME}.{module_name}.file_[ab]' \(.*"
            rf"{PACKAGE_NAME}[\\/]+{module_name}[\\/]+file_[ab]\.py\)"
        )
        with pytest.raises(ImportError, match=error_regex):
            assert_no_circular_imports()
    finally:
        # Clean up temporary files
        if os.path.exists(module_path):
            shutil.rmtree(module_path)
        sys.modules.pop(f"{PACKAGE_NAME}.{module_name}.file_a", None)
        sys.modules.pop(f"{PACKAGE_NAME}.{module_name}.file_b", None)
        sys.modules.pop(f"{PACKAGE_NAME}.{module_name}", None)


def test_circular_imports_present():
    _run_circular_import_test(
        "module_x",
        f"from {PACKAGE_NAME}.module_x.file_b import B",
        f"from {PACKAGE_NAME}.module_x.file_a import A",
    )


def test_circular_imports_present_with_relative_imports():
    # This test verifies that circular import detection works correctly when the problematic modules use
    # relative imports (e.g., `from .file_b import B`) rather than
    # absolute imports (e.g., `from starknet_py.module.file_b import B`),
    # which was tested in the previous test case.

    _run_circular_import_test(
        "module_y",
        "from .file_b import B",
        "from .file_a import A",
    )
