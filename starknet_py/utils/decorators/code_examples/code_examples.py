import re
from typing import Any


def add_code_examples(original_class: Any) -> Any:
    base_class = original_class.__base__
    for method_name, method in original_class.__dict__.items():
        file_name = "test_" + _camel_to_snake(original_class.__name__)
        docstring = f"""
        .. literalinclude:: ../starknet_py/tests/e2e/docs/code_examples/{file_name}.py
            :language: python
            :start-after: docs: {method_name.strip("_")}_start
            :end-before: docs: {method_name.strip("_")}_end
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
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
