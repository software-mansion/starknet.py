import warnings


def _print_deprecation_warning(message: str):
    warnings.simplefilter("default", DeprecationWarning)
    warnings.warn(message, category=DeprecationWarning, stacklevel=3)
