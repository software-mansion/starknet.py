import os
import time

from starkware.crypto.signature.signature import verify, private_to_stark_key

from starknet_py.utils.crypto.facade import (
    use_cpp_variant,
    hash_message,
    message_signature,
)


TEST_CRYPTO_LIB_PATH = os.getenv("TEST_CRYPTO_C_EXPORTS_PATH")


def test_hashing(monkeypatch):
    if not TEST_CRYPTO_LIB_PATH:
        return

    args = 1, 2, 3, [4, 5], 6

    times = []
    for _ in range(2):
        monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", TEST_CRYPTO_LIB_PATH)
        assert use_cpp_variant()
        start = time.time()
        hash_1 = hash_message(*args)
        end = time.time()
        time_with_crypto = end - start

        monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", "")
        assert not use_cpp_variant()
        start = time.time()
        hash_2 = hash_message(*args)
        end = time.time()
        time_without_crypto = end - start
        times.append((time_with_crypto, time_without_crypto))

        assert hash_1 == hash_2

    assert times[1][0] < times[1][1]
    assert times[0][0] < times[0][1]


def test_signing(monkeypatch):
    if not TEST_CRYPTO_LIB_PATH:
        return

    args = 1, 2
    msg_hash, priv_key = args

    times = []
    for _ in range(2):
        monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", TEST_CRYPTO_LIB_PATH)
        assert use_cpp_variant()
        start = time.time()
        signature_1 = message_signature(*args)
        end = time.time()
        time_with_crypto = end - start

        monkeypatch.setenv("CRYPTO_C_EXPORTS_PATH", "")
        assert not use_cpp_variant()
        start = time.time()
        signature_2 = message_signature(*args)
        end = time.time()
        time_without_crypto = end - start

        assert signature_1 == signature_2

        assert bool(verify(msg_hash, *signature_1, private_to_stark_key(priv_key)))
        assert bool(verify(msg_hash, *signature_2, private_to_stark_key(priv_key)))
        times.append((time_with_crypto, time_without_crypto))

    assert times[1][0] < times[1][1]
    assert times[0][0] < times[0][1]
