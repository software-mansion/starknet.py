from starknet_py.constants import EC_ORDER, FIELD_PRIME
from starknet_py.net.signer.key_pair import KeyPair


def test_generate_key_pair():
    key_pair = KeyPair.generate()
    assert 0 < key_pair.private_key < EC_ORDER
    assert 0 < key_pair.public_key < FIELD_PRIME
