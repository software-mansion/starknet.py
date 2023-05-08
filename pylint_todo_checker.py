import re
import tokenize

from pylint import checkers, interfaces


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(TodoTokenChecker(linter))


class TodoTokenChecker(checkers.BaseChecker):
    __implements__ = interfaces.ITokenChecker

    name = "todo-error"
    priority = -1
    msgs = {
        "E2137": (
            'Uses a "TODO" comment without specifying issue number.',
            "todo-error",
            "TODO comments should be in a format: `# TODO (#issueno)...`",
        ),
    }

    def process_tokens(self, tokens):
        for token in tokens:
            if token.type == tokenize.COMMENT:
                quotes_stripped = token.string.strip('"').strip("'")
                if "TODO" in quotes_stripped and not re.match(
                    "#\s*TODO\s*\(#\d+\).*", quotes_stripped
                ):
                    self.add_message("todo-error", line=token.start[0])
