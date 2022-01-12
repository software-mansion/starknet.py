import inspect
import os
import sys
from typing import TypeVar

generating_docs = os.path.basename(sys.argv[0]) == "sphinx-build"
T = TypeVar("T")


def as_our_module(cls: T) -> T:
    """
    We create alias for some function from starkware, but sphinx show original module path. This makes docs harder to
    follow.

    :param cls: class
    :return: Same class, just with changed module if docs are being created.
    """
    if not generating_docs:
        return cls

    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    cls.__module__ = mod.__name__
    return cls
