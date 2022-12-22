import pytest

from starknet_py.net import AccountClient


def test_account_client_init(gateway_client):
    with pytest.raises(ValueError, match="One of chain or signer must be provided."):
        _ = AccountClient(client=gateway_client, address=0)
