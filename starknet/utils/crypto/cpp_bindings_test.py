import os
from starknet.utils.crypto.facade import (
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

    monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", test_crypto_lib_path)
    assert use_cpp_variant()
    signature_1 = message_signature(*args)

    monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", "")
    assert not use_cpp_variant()
    signature_2 = message_signature(*args)

    assert signature_1 == signature_2
