import pytest
from crypto_cpp_py.cpp_bindings import (
    unload_cpp_lib,
    get_cpp_lib_file,
)
from starkware.crypto.signature.signature import verify, private_to_stark_key

from starknet_py.utils.crypto.facade import (
    use_cpp_variant,
    message_signature,
    compute_hash_on_elements,
)


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


@pytest.mark.parametrize(
    "data, calculated_hash",
    (
        (
            [1, 2, 3, 4, 5],
            3442134774288875752012730520904650962184640568595562887119811371865001706826,
        ),
        (
            [28, 15, 39, 74],
            1457535610401978056129941705021139155249904351968558303142914517100335003071,
        ),
    ),
)
def test_compute_hash_on_elements(data, calculated_hash):
    assert compute_hash_on_elements(data) == calculated_hash
