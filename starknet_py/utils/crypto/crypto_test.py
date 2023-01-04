from crypto_cpp_py.cpp_bindings import get_cpp_lib_file, unload_cpp_lib
from starkware.crypto.signature.signature import private_to_stark_key, verify

from starknet_py.utils.crypto.facade import message_signature, use_cpp_variant


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
