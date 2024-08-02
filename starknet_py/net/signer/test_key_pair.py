from starknet_py.net.signer.key_pair import KeyPair


def test_generate():
    key_pair = KeyPair.generate()
    assert len(hex(key_pair.private_key)) == 65
