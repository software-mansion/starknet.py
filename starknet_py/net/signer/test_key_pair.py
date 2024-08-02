from starknet_py.constants import FIELD_PRIME
from starknet_py.net.signer.key_pair import KeyPair


def test_generate():
    key_pair = KeyPair.generate()
    assert len(hex(key_pair.private_key)) == 65
    assert key_pair.private_key < FIELD_PRIME
    assert key_pair.public_key < FIELD_PRIME
