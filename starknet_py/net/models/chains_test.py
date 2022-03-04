import pytest

from starknet_py.net.models.chains import chain_from_network


def test_no_chain_for_custom_network():

    with pytest.raises(ValueError) as v_err:
        chain_from_network("some_custom_url", chain=None)

    assert "Chain is required when not using predefined networks." in str(v_err.value)
