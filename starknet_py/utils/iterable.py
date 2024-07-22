from typing import Iterable, TypeVar, Union

T = TypeVar("T")


def ensure_iterable(value: Union[T, Iterable[T]]) -> Iterable[T]:
    if isinstance(value, Iterable):
        return value
    return [value]
