# pylint: disable=import-outside-toplevel
import pytest

from starknet_py.constants import EC_ORDER, FIELD_PRIME


def test_generate_key_pair():
    # docs-generate: start
    from starknet_py.net.signer.key_pair import KeyPair

    key_pair = KeyPair.generate()
    # docs-generate: end

    assert 0 < key_pair.private_key < EC_ORDER
    assert 0 < key_pair.public_key < FIELD_PRIME


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
