from typing import TypeVar, Iterable, Union

T = TypeVar("T")

# pyright: reportGeneralTypeIssues=false
def ensure_iterable(value: Union[T, Iterable[T]]) -> Iterable[T]:
    try:
        iter(value)
        # Now we now it is iterable
        return value
    except TypeError:
        return [value]
