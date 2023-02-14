import importlib.util
import os
import sys


def _import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


def test_circular_imports():
    for path, subdirs, files in os.walk("starknet_py"):
        py_files = [f for f in files if f.endswith(".py")]
        for file_ in py_files:
            file_path = os.path.join(path, file_)
            _import_from_path(file_, file_path)
