import re
from typing import Any, Tuple

from starknet_py.constants import ROOT_PATH


def add_code_examples(original_class: Any) -> Any:
    base_class = original_class.__base__

    file_name, file_content = _extract_file_properties(original_class.__name__)

    for method_name, method in original_class.__dict__.items():
        stripped_method_name = method_name.strip("_")
        if f"""docs: {stripped_method_name}_start""" in file_content:
            hint = create_hint(file_name, stripped_method_name)

            # if method does not have __doc__ take it from the base method
            if (
                callable(method)
                and method.__doc__ is None
                and method_name in base_class.__dict__
            ):
                method.__doc__ = getattr(base_class, method_name).__doc__ + hint
            elif callable(method):
                method.__doc__ = (method.__doc__ or "") + hint

    return original_class


def create_hint(file_name: str, method_name: str) -> str:
    return f"""
        .. hint::
        
            .. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/{file_name}
                :language: python
                :start-after: docs: {method_name}_start
                :end-before: docs: {method_name}_end
                :dedent: 4
        """


def _extract_file_properties(class_name: str) -> Tuple[str, str]:
    file_name = "test_" + _camel_to_snake(class_name) + ".py"
    file_path = ROOT_PATH / "tests/e2e/docs/code_examples" / file_name

    with open(file_path, "r", encoding="utf-8") as file:
        return file_name, file.read()


def _camel_to_snake(text: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()
