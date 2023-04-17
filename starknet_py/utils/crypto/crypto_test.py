from crypto_cpp_py.cpp_bindings import get_cpp_lib_file, unload_cpp_lib
from starkware.crypto.signature.signature import private_to_stark_key, verify

from starknet_py.hash.utils import message_signature


def test_signing():
    args = 1, 2
    msg_hash, priv_key = args
    signature = message_signature(*args)

    assert bool(verify(msg_hash, *signature, private_to_stark_key(priv_key)))


def test_invalid_crypto_path(monkeypatch, mocker):
    unload_cpp_lib()
    monkeypatch.setenv("DISABLE_CRYPTO_C_EXTENSION", "")
    mocker.patch(
        "crypto_cpp_py.cpp_bindings.get_cpp_lib_path",
        return_value="/an/nonexisting/directory",
    )

    file = get_cpp_lib_file()
    assert file is None
