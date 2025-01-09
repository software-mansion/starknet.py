import functools
import warnings


def deprecated(message):
    warnings.simplefilter("default", DeprecationWarning)

    def _deprecated_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated and will be removed in future versions. {message}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return _deprecated_decorator
