from contextlib import contextmanager
from typing import List, Generator

from starknet_py.utils.data_transformer._calldata_reader import OutOfBoundsError
from starknet_py.utils.data_transformer.errors import (
    InvalidTypeException,
    InvalidValueException,
)


class TransformationContext:
    """
    Holds information about context when transforming data. This is needed to inform what and where went wrong during
    transformation. Every transformation should have its own transformation context.
    """

    _namespace_stack: List[str]

    @property
    def current_entity(self):
        """
        Name of currently processed entity.

        :return: transformed path.
        """
        return ".".join(self._namespace_stack)

    @contextmanager
    def push_entity(self, name: str) -> Generator:
        """
        Manager used for maintaining information about names of transformed types. Will wrap some errors with
        custom errors, adding information about the context.

        :param name: name of transformed entity.
        """
        self._namespace_stack.append(name)
        try:
            yield
        except OutOfBoundsError as err:
            # This way we can precisely inform user what's wrong when reading calldata.
            raise InvalidValueException(
                f"Not enough data to deserialize '{self.current_entity}'. "
                f"Can't read {err.requested_size} values at position {err.position}, only {err.remaining_len} available"
            ) from err
        except ValueError as err:
            # This is needed to allow libraries dependent on data transformers to catch all issues related to it.
            raise InvalidValueException(
                f"Error at '{self.current_entity}': {err}"
            ) from err
        except TypeError as err:
            # This is needed to allow libraries dependent on data transformers to catch all issues related to it.
            raise InvalidTypeException(
                f"Error at '{self.current_entity}': {err}"
            ) from err
        finally:
            self._namespace_stack.pop()

    def ensure_valid_value(self, valid: bool, text: str):
        if not valid:
            raise InvalidValueException(f"Error at '{self.current_entity}': {text}")

    def ensure_valid_type(self, valid: bool, expected_type: str):
        if not valid:
            raise InvalidTypeException(
                f"Type of {self.current_entity} must be {expected_type}"
            )
