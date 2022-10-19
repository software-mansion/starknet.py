import pytest


def test_warns_about_deprecation():
    with pytest.warns(
        DeprecationWarning,
        match=r"Importing from starknet_py.net.client_models has been deprecated.",
    ):
        # pylint: disable=unused-import, import-outside-toplevel
        import starknet_py.net.client_models
