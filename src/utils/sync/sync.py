import inspect
from functools import wraps
from typing import Type, TypeVar

from asgiref.sync import async_to_sync

T = TypeVar("T")


def add_sync_version(original_class: T) -> T:
    """
    Decorator for adding a synchronous version of a class.
    :param original_class: Input class
    :return: Input class with .sync property that contains synchronous version of this class
    """
    properties = original_class.__dict__
    synchronous_properties = {}
    for name, value in properties.items():
        # Adding it would result TypeError
        if name == "__dict__":
            continue

        # Constructor might be assigning some async instances
        if name == "__init__":
            value = make_sync_init(value)

        # Make all callables synchronous
        if inspect.iscoroutinefunction(value):
            value = make_sync(value)
        if isinstance(value, staticmethod):
            value = staticmethod(make_sync(value.__func__))
        if isinstance(value, classmethod):
            value = classmethod(make_sync(value.__func__))

        synchronous_properties[name] = value

    synchronous_version = type(
        make_sync_class_name(original_class),
        original_class.__bases__,
        synchronous_properties,
    )
    original_class.sync = synchronous_version

    return original_class


def is_async_class(cls: Type) -> bool:
    """
    Checks if class has a synchronous version.
    :param cls: Class
    :return: bool
    """
    return (
        hasattr(cls, "sync")
        and inspect.isclass(cls.sync)
        and make_sync_class_name(cls) == cls.sync.__name__
    )


def is_async_instance(val: any) -> bool:
    """
    Checks if instance's class has a synchronous version
    :param val: any
    :return: bool
    """
    return is_async_class(val.__class__)


def make_sync_class_name(cls: Type) -> str:
    return "Sync" + cls.__name__


def make_sync(fn):
    sync_fun = async_to_sync(fn)

    @wraps(fn)
    def impl(*args, **kwargs):
        result = sync_fun(*args, **kwargs)
        return maybe_make_instance_sync(result)

    return impl


def maybe_make_instance_sync(value):
    if not is_async_instance(value):
        return value

    make_all_properties_sync(value)
    # Switch initial class
    # setattr doesn't work with frozen dataclasses
    object.__setattr__(value, "__class__", value.__class__.sync)

    return value


def make_sync_init(original):
    """
    Creates a replacement __init__ function to replace all properties with sync versions.
    """

    def __init__(self, *args, **kwargs):
        original(self, *args, **kwargs)
        make_all_properties_sync(self)

    return __init__


def make_all_properties_sync(instance):
    for name, value in instance.__dict__.items():
        instance.__dict__[name] = maybe_make_instance_sync(value)
