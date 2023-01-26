import re
from typing import Any, Dict, List, Tuple

from docutils import nodes
from docutils.nodes import Element, Node
from docutils.parsers.rst import directives
from sphinx.directives import optional_int
from sphinx.directives.code import LiteralIncludeReader
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec


def valid_code_snippet(code_snippet: List[str]) -> bool:
    """Check if code_snippet is non-empty"""
    return len(code_snippet) > 0


class CodeSnippet(SphinxDirective):
    """
    Directive class that allows multiple uses of :start-after: and :end-before: options
    """

    default_start_marker = "docs: start"
    default_end_marker = "docs: end"

    has_content = False  # No content, like a block of code, in the directive
    required_arguments = 1  # Source file path is needed
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec: OptionSpec = {
        "dedent": optional_int,
        "language": directives.unchanged_required,
        "start-after": directives.unchanged_required,
        "end-before": directives.unchanged_required,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.end_marker = None
        self.location = None
        self.filename = None
        self.reader = None

    def run(self) -> List[Node]:
        self._set_options()
        self._set_locals()
        code_snippets = self._get_code_snippets()
        return [self._make_node(code_snippets)]

    def _get_code_snippets(self) -> List[str]:
        lines = self.reader.read_file(self.filename, self.location)
        result = []

        while True:
            code_snippet, lines = self._get_code_snippet(lines)
            if not valid_code_snippet(code_snippet):
                break
            result.extend(code_snippet)
        return result

    def _get_code_snippet(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """Returns the first code snippet from lines and the rest of lines after that"""
        try:
            code_snippet_to_end = self._end_filter(lines)
            lines = lines[len(code_snippet_to_end) :]
            code_snippet_start_to_end = self._start_filter(code_snippet_to_end)
            code_snippet = self.reader.dedent_filter(
                code_snippet_start_to_end, self.location
            )
        except ValueError as err:
            if "pattern not found" in str(err):
                return [], []
            raise err
        return code_snippet, lines

    def _end_filter(self, lines: List[str]) -> List[str]:
        end = self.options["end-before"]
        pattern = rf"(?<!\S){end}(?!\S)"

        for lineno, line in enumerate(lines[1:], start=1):
            if re.search(pattern, line):
                return lines[:lineno]

        raise ValueError(f"end-before pattern not found: {end}")

    def _start_filter(self, lines: List[str]) -> List[str]:
        start = self.options["start-after"]
        pattern = rf"(?<!\S){start}(?!\S)"

        for lineno, line in enumerate(lines):
            if re.search(pattern, line):
                self._fix_lineno_start(lineno)
                return lines[lineno + 1 :]

        raise ValueError(f"start-after pattern not found: {start}")

    def _fix_lineno_start(self, lineno):
        if "lineno-match" in self.options:
            self.lineno_start += lineno + 1

    def _set_options(self) -> None:
        self.options["start-after"] = self.options.get(
            "start-after", self.default_start_marker
        )
        self.options["end-before"] = self.options.get(
            "end-before", self.default_end_marker
        )

    def _set_locals(self) -> None:
        self.end_marker = self._get_end_marker()
        self.location = self._get_location()
        self.filename = self._get_filename()
        self.reader = LiteralIncludeReader(self.filename, self.options, self.config)

    def _get_end_marker(self) -> str:
        return self.options["end-before"]

    def _get_location(self) -> Tuple[str, int]:
        return self.state_machine.get_source_and_line(self.lineno)

    def _get_filename(self) -> str:
        rel_filename, filename = self.env.relfn2path(self.arguments[0])
        self.env.note_dependency(rel_filename)
        return filename

    def _make_node(self, code_snippets) -> Node:
        text = "".join(code_snippets)
        node: Element = nodes.literal_block(text, text, source=self.filename)

        if "language" in self.options:
            node["language"] = self.options["language"]
        return node


def setup(app) -> Dict[str, Any]:
    app.add_directive("codesnippet", CodeSnippet)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
