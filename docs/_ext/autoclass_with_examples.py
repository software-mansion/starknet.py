import re
import sys
from typing import Any, Dict, List, Tuple

from docutils.nodes import Node
from sphinx.ext.autodoc.directive import AutodocDirective

from starknet_py.constants import ROOT_PATH


class AutoclassWithExamples(AutodocDirective):
    """
    Directive class extending AutodocDirective and adding code examples.
    """

    def run(self) -> List[Node]:
        original_class = getattr(
            sys.modules[self.env.ref_context.get("py:module")], self.arguments[0]
        )
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
            hint = create_hint(file_name, stripped_method_name)

            # if method does not have __doc__ take it from the base method
            if method.__doc__ is None and method_name in base_class.__dict__:
                method.__doc__ = getattr(base_class, method_name).__doc__ + hint
            else:
                method.__doc__ = (method.__doc__ or "") + hint


def _code_example_exists(method_name: str, file_content: str):
    return f"""test_{method_name}(""" in file_content


def create_hint(file_name: str, method_name: str) -> str:
    """
    Constructs a hint with code example.
    """
    return f"""
        .. hint::

            .. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/{file_name}
                :language: python
                :start-after: docs-start: {method_name}
                :end-before: docs-end: {method_name}
                :dedent: 4
        """


def _extract_file_properties(class_name: str) -> Tuple[str, str]:
    """
    Extracts file content for given class name.

    :param class_name: A string representing the name of the class where examples will be added to.
    :returns: A tuple containing the name of the file as a string, and its content as a string.
    """
    file_name = "test_" + _camel_to_snake(class_name) + ".py"
    file_path = ROOT_PATH / "tests/e2e/docs/code_examples" / file_name

    with open(file_path, "r", encoding="utf-8") as file:
        return file_name, file.read()


def _camel_to_snake(text: str) -> str:
    """
    Transforms camelCase to the snake_case.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def setup(app) -> Dict[str, Any]:
    app.add_directive("autoclass-with-examples", AutoclassWithExamples)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
