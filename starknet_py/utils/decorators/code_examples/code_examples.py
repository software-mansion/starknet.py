import re
from pathlib import Path
from typing import Any

CODE_EXAMPLES_DIR = Path("../starknet_py/tests/e2e/docs/code_examples")


def add_code_examples(original_class: Any) -> Any:
    base_class = original_class.__base__
    file_name = "test_" + _camel_to_snake(original_class.__name__) + ".py"
    file_path = CODE_EXAMPLES_DIR / file_name

    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    for method_name, method in original_class.__dict__.items():
        stripped_method_name = method_name.strip("_")
        if f"""docs: {stripped_method_name}_start""" in file_content:
            docstring = f"""
            .. hint::
            
                .. codesnippet:: {".." / file_path}
                    :language: python
                    :start-after: docs: {stripped_method_name}_start
                    :end-before: docs: {stripped_method_name}_end
                    :dedent: 4
            """

            # if method does not have __doc__ take it from the base method
            if (
                callable(method)
                and method.__doc__ is None
                and method_name in base_class.__dict__
            ):
                method.__doc__ = getattr(base_class, method_name).__doc__ + docstring
            elif callable(method):
                method.__doc__ = (method.__doc__ or "") + docstring

    return original_class


def _camel_to_snake(text: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()
