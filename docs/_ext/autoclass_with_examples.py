import re
from importlib import import_module
from typing import Any, Dict, List, Tuple

from docutils.nodes import Node
from sphinx.ext.autodoc.directive import AutodocDirective

from starknet_py.constants import ROOT_PATH


class AutoclassWithExamples(AutodocDirective):
    """
    Custom extension of the AutodocDirective class, which is used to
    add code examples to the method docstrings in the documentation.

    This class runs before the AutodocDirective class and pulls code snippets
    from the starknet_py/tests/e2e/docs/code_examples directory to include in the documentation.
    This allows developers to easily see and understand how the methods
    being documented are intended to be used in a practical context.

    .. note::

        The docstrings will not be inherited if the hierarchy is `deeper` than one step.
    """

    def run(self) -> List[Node]:
        # Gets the module by its path.
        # Path is stored in the self.env.ref_context
        module_name = self.env.ref_context.get("py:module")
        module = import_module(module_name)

        # Gets class from imported module
        # Name of the class is passed as an argument
        original_class = getattr(module, self.arguments[0])
        add_code_examples(original_class)

        self.name = self.name.replace("-with-examples", "")  # remove `-with-examples`

        return AutodocDirective.run(self)


def add_code_examples(original_class: Any):
    """
    Adds code examples for the given class.
    """
    base_class = original_class.__base__

    file_name, file_content = _extract_file_properties(original_class.__name__)

    for method_name, method in original_class.__dict__.items():
        if not callable(method):
            continue

        stripped_method_name = method_name.strip("_")
        if _code_example_exists(stripped_method_name, file_content):
            hint = _create_hint(file_name, stripped_method_name)
            _append_hint(method_name, method, base_class, hint)


def _extract_file_properties(class_name: str) -> Tuple[str, str]:
    """
    Extracts file content for given class name.

    :param class_name: A string representing the name of the class where examples will be added to.
    :returns: A tuple containing the name of the file as a string, and its content as a string.
    """
    file_name = "test_" + _camel_to_snake(class_name) + ".py"
    file_path = ROOT_PATH / "tests/e2e/docs/code_examples" / file_name

    return file_name, file_path.read_text("utf-8")


def _camel_to_snake(text: str) -> str:
    """
    Transforms camelCase to the snake_case.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def _code_example_exists(method_name: str, file_content: str):
    return f"test_{method_name}(" in file_content


def _create_hint(file_name: str, method_name: str) -> str:
    """
    Constructs a hint with code example.
    """
    return f"""
        .. admonition:: Example
            :class: hint

            .. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/{file_name}
                :language: python
                :start-after: docs-start: {method_name}
                :end-before: docs-end: {method_name}
                :dedent: 4
        """


def _append_hint(method_name: str, method, base_class: Any, hint: str):
    """
    If method does not have the __doc__, takes it from the base method.
    """
    if method.__doc__ is None and method_name in base_class.__dict__:
        method.__doc__ = getattr(base_class, method_name).__doc__ + hint
    else:
        method.__doc__ = (method.__doc__ or "") + hint


def setup(app) -> Dict[str, Any]:
    app.add_directive("autoclass-with-examples", AutoclassWithExamples)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
