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
    print(f"module_name: {module_name}, file_path: {file_path}")
    spec.loader.exec_module(module)


def assert_no_circular_imports():
    for path, _, files in os.walk(PACKAGE_NAME):
        for f in files:
            if not f.endswith(".py"):
                continue

            file_path = os.path.join(path, f)

            rel = os.path.relpath(file_path, PACKAGE_NAME)
            rel_no_ext = rel.removesuffix(".py")
            dotted = rel_no_ext.replace(os.sep, ".")
            module_name = f"{PACKAGE_NAME}.{dotted}"

            _import_from_path(module_name, file_path)


def test_circular_imports_absent():
    assert_no_circular_imports()


def test_circular_imports_present():
    # Create temporary files which cause circular imports
    os.makedirs(f"{PACKAGE_NAME}/temp_module", exist_ok=True)
    with open(f"{PACKAGE_NAME}/temp_module/file_a.py", "w") as f:
        f.write(
            f"from {PACKAGE_NAME}.temp_module.file_b import B\nclass A:\n    pass\n"
        )

    with open(f"{PACKAGE_NAME}/temp_module/file_b.py", "w") as f:
        f.write(
            f"from {PACKAGE_NAME}.temp_module.file_a import A\nclass B:\n    pass\n"
        )

    error_regex = (
        rf"cannot import name 'B' from '{PACKAGE_NAME}.temp_module.file_b' (.*"
        rf"/{PACKAGE_NAME}/temp_module/file_b.py)"
    )
    with pytest.raises(ImportError, match=error_regex):
        assert_no_circular_imports()

    # Clean up temporary files
    shutil.rmtree(f"{PACKAGE_NAME}/temp_module")


def test_circular_imports_present_with_relative_imports():
    # In this case, we use relative imports
    # Create temporary files which cause circular imports
    os.makedirs(f"{PACKAGE_NAME}/temp_module", exist_ok=True)
    with open(f"{PACKAGE_NAME}/temp_module/file_a.py", "w") as f:
        f.write(f"from .file_b import B\nclass A:\n    pass\n")

    with open(f"{PACKAGE_NAME}/temp_module/file_b.py", "w") as f:
        f.write(f"from .file_a import A\nclass B:\n    pass\n")

    error_regex = (
        rf"cannot import name 'B' from '{PACKAGE_NAME}.temp_module.file_b' (.*"
        rf"/{PACKAGE_NAME}/temp_module/file_b.py)"
    )
    with pytest.raises(ImportError, match=error_regex):
        assert_no_circular_imports()

    # Clean up temporary files
    shutil.rmtree(f"{PACKAGE_NAME}/temp_module")
