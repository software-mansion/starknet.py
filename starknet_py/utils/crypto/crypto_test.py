import time
from starkware.crypto.signature.signature import verify, private_to_stark_key

from crypto_cpp_py.cpp_bindings import (
    unload_cpp_lib,
    get_cpp_lib_file,
    load_cpp_lib,
)
from starknet_py.utils.crypto.facade import (
    MultiCall,
    Call,
    use_cpp_variant,
    hash_multicall,
    message_signature,
)


def test_hashing(monkeypatch):
    call = Call(to_addr=1, selector=2, calldata=[4, 5])
    multi_call = MultiCall(account=3, calls=[call], nonce=6)
    times = []

    load_cpp_lib()  # Pre-load cpp extension to make the hashing time appropriate
    for _ in range(2):
        monkeypatch.setenv("DISABLE_CRYPTO_C_EXTENSION", "")

        assert use_cpp_variant()
        start = time.time()
        hash_1 = hash_multicall(multi_call)
        end = time.time()
        time_with_crypto = end - start

        monkeypatch.setenv("DISABLE_CRYPTO_C_EXTENSION", "true")
        assert not use_cpp_variant()
        start = time.time()
        hash_2 = hash_multicall(multi_call)
        end = time.time()
        time_without_crypto = end - start
        times.append((time_with_crypto, time_without_crypto))

        assert hash_1 == hash_2

    assert times[1][0] < times[1][1]
    assert times[0][0] < times[0][1]


def test_signing(monkeypatch):
    args = 1, 2
    msg_hash, priv_key = args
    monkeypatch.setenv("DISABLE_CRYPTO_C_EXTENSION", "")
    assert use_cpp_variant()
    signature_1 = message_signature(*args)

    monkeypatch.setenv("DISABLE_CRYPTO_C_EXTENSION", "true")
    assert not use_cpp_variant()
    signature_2 = message_signature(*args)

    assert signature_1 == signature_2

    assert bool(verify(msg_hash, *signature_1, private_to_stark_key(priv_key)))
    assert bool(verify(msg_hash, *signature_2, private_to_stark_key(priv_key)))


def test_invalid_crypto_path(monkeypatch, mocker):
    unload_cpp_lib()
    monkeypatch.setenv("DISABLE_CRYPTO_C_EXTENSION", "")
    mocker.patch(
        "crypto_cpp_py.cpp_bindings.get_cpp_lib_path",
        return_value="/an/nonexisting/directory",
    )

    file = get_cpp_lib_file()
    assert file is None
