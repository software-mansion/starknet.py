from typing import List, Dict, Any

from docutils import nodes
from docutils.nodes import Element, Node
from docutils.parsers.rst import directives
from sphinx.directives import optional_int
from sphinx.directives.code import LiteralIncludeReader
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec


def valid_code_snippet(code_snippet: List[str]) -> bool:
    return len(code_snippet) > 0


def remove_code_snippet(lines, end_marker) -> List[str]:
    for idx, line in enumerate(lines):
        if end_marker in line:
            return lines[idx + 1:]
    return []


def get_code_snippet(lines, filters, location) -> List[str]:
    code_snippet = lines
    try:
        for func in filters:
            code_snippet = func(code_snippet, location=location)
    except ValueError as err:
        if "pattern not found" in str(err):
            return []
        raise err
    return code_snippet


class CodeSnippet(SphinxDirective):
    """
    Directive class that allows multiple uses of :start-after: and :end-before: options
    """
    default_start = "docs: start"
    default_end = "docs: end"

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec: OptionSpec = {
        "dedent": optional_int,
        "language": directives.unchanged_required,
        "start-after": directives.unchanged_required,
        "end-before": directives.unchanged_required,
    }

    def run(self) -> List[Node]:
        self._set_options()
        end_marker = self._get_end_marker()
        filename = self._get_filename()
        code_snippets = self._get_code_snippets(filename, end_marker)
        return [self._make_node(code_snippets, filename)]

    def _get_code_snippets(self, filename: str, end_marker: str) -> List[str]:
        location = self.state_machine.get_source_and_line(self.lineno)
        reader = LiteralIncludeReader(filename, self.options, self.config)
        lines = reader.read_file(filename, location=location)

        filters = [reader.start_filter, reader.end_filter, reader.dedent_filter]
        result = []

        while True:
            code_snippet = get_code_snippet(lines, filters, location)
            if not valid_code_snippet(code_snippet):
                break

            result.extend(code_snippet)
            lines = remove_code_snippet(lines, end_marker)
        return result

    def _get_end_marker(self) -> str:
        if "end-before" not in self.options:
            raise ValueError("end-before pattern not found")
        return self.options["end-before"]

    def _get_filename(self) -> str:
        rel_filename, filename = self.env.relfn2path(self.arguments[0])
        self.env.note_dependency(rel_filename)
        return filename

    def _make_node(self, code_snippets, filename) -> Node:
        text = "".join(code_snippets)
        node: Element = nodes.literal_block(text, text, source=filename)

        if "language" in self.options:
            node["language"] = self.options["language"]
        return node

    def _set_options(self) -> None:
        self.options["start-after"] = self.options.get("start-after", self.default_start)
        self.options["end-before"] = self.options.get("end-after", self.default_end)


def setup(app) -> Dict[str, Any]:
    app.add_directive("codesnippet", CodeSnippet)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
