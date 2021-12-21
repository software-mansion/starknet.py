import os

from starkware.crypto.signature.signature import verify, private_to_stark_key

from starknet_py.utils.crypto.facade import (
    use_cpp_variant,
    hash_message,
    message_signature,
)

test_crypto_lib_path = os.environ.get("CRYPTO_C_EXPORTS_PATH_TEST")


def crypto_lib_present() -> bool:
    return test_crypto_lib_path and os.path.isfile(test_crypto_lib_path)


def test_hashing(monkeypatch):
    if not crypto_lib_present():
        return

    args = 1, 2, 3, [4, 5], 6

    monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", test_crypto_lib_path)
    assert use_cpp_variant()
    hash_1 = hash_message(*args)

    monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", "")
    assert not use_cpp_variant()
    hash_2 = hash_message(*args)

    assert hash_1 == hash_2


def test_signing(monkeypatch):
    if not crypto_lib_present():
        return

    args = 1, 2
    msg_hash, priv_key = args

    monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", test_crypto_lib_path)
    assert use_cpp_variant()
    signature_1 = message_signature(*args)

    monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", "")
    assert not use_cpp_variant()
    signature_2 = message_signature(*args)

    assert signature_1 == signature_2

    assert bool(verify(msg_hash, *signature_1, private_to_stark_key(priv_key)))
    assert bool(verify(msg_hash, *signature_2, private_to_stark_key(priv_key)))
