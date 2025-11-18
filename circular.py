import importlib.util
import os
import sys

PACKAGE_ROOT = "starknet_py"


# def _import_from_path(module_name, file_path):
#     spec = importlib.util.spec_from_file_location(module_name, file_path)
#     module = importlib.util.module_from_spec(spec)
#     print(f"Importing module: {module_name} from {file_path}")
#     sys.modules[module_name] = module
#     spec.loader.exec_module(module)


def test_circular_imports():
    for path, _, files in os.walk(PACKAGE_ROOT):
        py_files = [f for f in files if f.endswith(".py")]
        for file_ in py_files:
            file_path = os.path.join(path, file_)
            # _import_from_path(file_, file_path)
            _import_from_path(file_path)


def _import_from_path(file_path):
    if not file_path.startswith(PACKAGE_ROOT):
        return

    # Remove 'starknet_py/' and '.py'
    module_name = file_path[len(PACKAGE_ROOT) + 1 : -3]

    # Change "/" to "." (e.g. serialization/__init__ -> serialization.__init__)
    module_name = module_name.replace(os.sep, ".")

    # If module is __init__, remove it from the name (serialization.__init__ -> serialization)
    if module_name.endswith(".__init__"):
        module_name = module_name[:-9]

    # Bring back the main package (e.g. serialization -> starknet_py.serialization)
    full_module_name = f"{PACKAGE_ROOT}.{module_name}"

    spec = importlib.util.spec_from_file_location(full_module_name, file_path)
    module = importlib.util.module_from_spec(spec)

    print(f"Importing module: {full_module_name} from {file_path}")
    sys.modules[full_module_name] = module
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    spec.loader.exec_module(module)
