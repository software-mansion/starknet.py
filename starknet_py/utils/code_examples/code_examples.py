from starknet_py.utils.sync.sync import T


def add_code_examples(original_class) -> T:
    base_class = original_class.__base__  # pyright: ignore
    for method_name, method in original_class.__dict__.items():
        docstring = f"""
        .. literalinclude:: ../starknet_py/tests/e2e/docs/code_examples/test_{original_class.__name__}.py
            :language: python
            :start-after: docs: {method_name.strip("_")}_start
            :end-before: docs: {method_name.strip("_")}_end
            :dedent: 4
        """

        if (
            callable(method)
            and method.__doc__ is None
            and method_name in base_class.__dict__
        ):
            method.__doc__ = getattr(base_class, method_name).__doc__ + docstring
        elif callable(method):
            method.__doc__ = (method.__doc__ or "") + docstring

    return original_class
