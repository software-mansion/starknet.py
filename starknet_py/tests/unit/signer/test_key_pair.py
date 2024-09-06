from starknet_py.constants import FIELD_PRIME
from starknet_py.net.signer.key_pair import KeyPair


def test_generate_key_pair():
    key_pair = KeyPair.generate()
    hex_private_key = hex(key_pair.private_key)[2:]
    padded_hex_private_key = hex_private_key.zfill(64)
    assert len(padded_hex_private_key) == 64
    assert key_pair.private_key < FIELD_PRIME
    assert key_pair.public_key < FIELD_PRIME
