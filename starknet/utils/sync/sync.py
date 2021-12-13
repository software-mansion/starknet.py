import inspect
from typing import TypeVar

from asgiref.sync import async_to_sync

T = TypeVar("T")


def add_sync_methods(original_class: T) -> T:
    """
    Decorator for adding a synchronous version of a class.
    :param original_class: Input class
    :return: Input class with .sync property that contains synchronous version of this class
    """
    properties = {**original_class.__dict__}
    for name, value in properties.items():
        sync_name = name + "_sync"

        # Hand written implementation exists
        if sync_name in properties:
            continue

        # Make all callables synchronous
        if inspect.iscoroutinefunction(value):
            value = async_to_sync(value)
        elif isinstance(value, staticmethod) and inspect.iscoroutinefunction(
            value.__func__
        ):
            value = staticmethod(async_to_sync(value.__func__))
        elif isinstance(value, classmethod) and inspect.iscoroutinefunction(
            value.__func__
        ):
            value = classmethod(async_to_sync(value.__func__))
        else:
            continue

        setattr(original_class, sync_name, value)

    return original_class
