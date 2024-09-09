# pylint: disable=import-outside-toplevel
import pytest

from starknet_py.constants import FIELD_PRIME


def test_generate_key_pair():
    # docs-generate: start
    from starknet_py.net.signer.key_pair import KeyPair

    key_pair = KeyPair.generate()
    # docs-generate: end

    hex_private_key = hex(key_pair.private_key)[2:]
    padded_hex_private_key = hex_private_key.zfill(64)
    assert len(padded_hex_private_key) == 64
    assert key_pair.private_key < FIELD_PRIME
    assert key_pair.public_key < FIELD_PRIME


def test_key_pair_from_private_key():
    # docs-from-private-key: start
    from starknet_py.net.signer.key_pair import KeyPair

    key_pair = KeyPair.from_private_key("0x1234abcd")
    # docs-from-private-key: end

    assert isinstance(key_pair.public_key, int)
    assert isinstance(key_pair.private_key, int)


@pytest.mark.skip(reason="This test requires a keystore file")
def test_key_pair_from_keystore():
    # docs-from-keystore: start
    from starknet_py.net.signer.key_pair import KeyPair

    key_pair = KeyPair.from_keystore("path/to/keystore", "password")
    # docs-from-keystore: end

    assert isinstance(key_pair.public_key, int)
    assert isinstance(key_pair.private_key, int)
