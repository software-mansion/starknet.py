import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner, KeyPair


def test_create_account_without_signer_and_chain(gateway_client):
    with pytest.raises(ValueError) as exinfo:
        Account(address=0x123, client=gateway_client)

    assert "One of chain or signer must be provided" in str(exinfo.value)


def test_create_account_without_signer_and_keypair(gateway_client):
    with pytest.raises(ValueError) as exinfo:
        Account(address=0x123, client=gateway_client, chain=StarknetChainId.TESTNET)

    assert (
        "Either a signer or a key_pair must be provided in AccountClient constructor"
        in str(exinfo.value)
    )


def test_create_account_with_signer(gateway_client):
    signer = StarkCurveSigner(
        account_address=0x123,
        chain_id=StarknetChainId.TESTNET,
        key_pair=KeyPair.from_private_key(0x111),
    )
    assert Account(address=0x123, client=gateway_client, signer=signer)


def test_create_account_with_keypair(gateway_client):
    assert Account(
        address=0x123,
        client=gateway_client,
        key_pair=KeyPair.from_private_key(0x111),
        chain=StarknetChainId.TESTNET,
    )
