from __future__ import annotations

from abc import ABC
from contextlib import contextmanager
from typing import List, Generator, ContextManager, Any

from starknet_py.cairo.serialization._calldata_reader import (
    OutOfBoundsError,
    CalldataReader,
    CairoData,
)
from starknet_py.cairo.serialization.errors import (
    InvalidValueException,
    InvalidTypeException,
)


class Context(ABC):
    """
    Holds information about context when (de)serializing data. This is needed to inform what and where went
    wrong during processing. Every separate (de)serialization should have its own context.
    """

    _namespace_stack: List[str]

    def __init__(self):
        self._namespace_stack = []

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
        Manager used for maintaining information about names of (de)serialized types. Wraps some errors with
        custom errors, adding information about the context.

        :param name: name of (de)serialized entity.
        """
        # This ensures the name will be popped if everything is ok. In case an exception is raised we want the stack to
        # be filled to wrap the error at the end.
        self._namespace_stack.append(name)
        yield
        self._namespace_stack.pop()

    def ensure_valid_value(self, value: Any, valid: bool, text: str):
        if not valid:
            raise InvalidValueException(
                f"{self._error_prefix}: invalid value '{value}' - {text}."
            )

    def ensure_valid_type(self, value: Any, valid: bool, expected_type: str):
        if not valid:
            raise InvalidTypeException(
                f"{self._error_prefix}: expected {expected_type}, "
                f"received '{value}' of type '{type(value)}'."
            )

    @contextmanager
    def _wrap_errors(self) -> ContextManager:
        try:
            yield
        except OutOfBoundsError as err:
            # This way we can precisely inform user what's wrong when reading calldata.
            raise InvalidValueException(
                f"{self._error_prefix}: not enough data to deserialize. "
                f"Can't read {err.requested_size} values at position {err.position}, {err.remaining_len} available."
            ) from err

        # Those two are based on ValueError and TypeError, we have to catch them early
        except (InvalidValueException, InvalidTypeException) as err:
            raise err

        except ValueError as err:
            raise InvalidValueException(f"{self._error_prefix}: {err}") from err
        except TypeError as err:
            raise InvalidTypeException(f"{self._error_prefix}: {err}") from err

    @property
    def _error_prefix(self):
        if not self._namespace_stack:
            return "Error"
        return f"Error at path '{self.current_entity}'"


class SerializationContext(Context):
    """
    Context used during serialization.
    """

    @classmethod
    @contextmanager
    def create(cls) -> ContextManager[SerializationContext]:
        context = cls()
        with context._wrap_errors():
            yield context


class DeserializationContext(Context):
    """
    Context used during deserialization.
    """

    reader: CalldataReader

    def __init__(self, calldata: CairoData):
        """
        Don't use default constructor. Use DeserializationContext.create context manager.
        """
        super().__init__()
        self._namespace_stack = []
        self.reader = CalldataReader(calldata)

    @classmethod
    @contextmanager
    def create(cls, data: CairoData) -> ContextManager[DeserializationContext]:
        context = cls(data)
        with context._wrap_errors():
            yield context
            values_not_used = context.reader.remaining_len
            if values_not_used != 0:
                raise ValueError(
                    f"{values_not_used} values out of total {len(data)} values were not used during deserialization."
                )
