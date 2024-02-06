import re
import tokenize

from pylint import checkers, interfaces


def register(linter: "PyLinter") -> None:
    """
    This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(TodoTokenChecker(linter))


class TodoTokenChecker(checkers.BaseTokenChecker):
    name = "todo-issue-error"
    priority = -1
    msgs = {
        "E2137": (
            "Invalid TODO format, should be: '# TODO (#issue number): ...'.",
            name,
            "TODO comments should be in a format: '# TODO (#issue number): ...'.",
        ),
    }

    def process_tokens(self, tokens):
        for token in tokens:
            if token.type == tokenize.COMMENT:
                quotes_stripped = token.string.strip('"').strip("'")
                if "TODO" in quotes_stripped and not re.match(
                    "#\s*TODO\s*\(#\d+\):.*", quotes_stripped
                ):
                    self.add_message(self.name, line=token.start[0])
