import ctypes
import os
from typing import Optional, Tuple

from starkware.crypto.signature.signature import inv_mod_curve_size, generate_k_rfc6979

CPP_LIB_BINDING = None
OUT_BUFFER_SIZE = 251


def get_cpp_lib(crypto_c_exports_path):
    # pylint: disable=global-statement
    global CPP_LIB_BINDING
    if CPP_LIB_BINDING:
        return
    CPP_LIB_BINDING = ctypes.cdll.LoadLibrary(os.path.abspath(crypto_c_exports_path))
    # Configure argument and return types.
    CPP_LIB_BINDING.Hash.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    CPP_LIB_BINDING.Verify.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    CPP_LIB_BINDING.Verify.restype = bool
    CPP_LIB_BINDING.Sign.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]


def cpp_binding_loaded() -> bool:
    return CPP_LIB_BINDING is not None


# A type for the digital signature.
ECSignature = Tuple[int, int]


def cpp_hash(left: int, right: int) -> int:
    res = ctypes.create_string_buffer(OUT_BUFFER_SIZE)
    if (
        CPP_LIB_BINDING.Hash(
            left.to_bytes(32, "little", signed=False),
            right.to_bytes(32, "little", signed=False),
            res,
        )
        != 0
    ):
        raise ValueError(res.raw.rstrip(b"\00"))
    return int.from_bytes(res.raw[:32], "little", signed=False)


def cpp_sign(msg_hash, priv_key, seed: Optional[int] = 32) -> ECSignature:
    res = ctypes.create_string_buffer(OUT_BUFFER_SIZE)
    k = generate_k_rfc6979(msg_hash, priv_key, seed)
    if (
        CPP_LIB_BINDING.Sign(
            priv_key.to_bytes(32, "little", signed=False),
            msg_hash.to_bytes(32, "little", signed=False),
            k.to_bytes(32, "little", signed=False),
            res,
        )
        != 0
    ):
        raise ValueError(res.raw.rstrip(b"\00"))
    # pylint: disable=invalid-name
    w = int.from_bytes(res.raw[32:64], "little", signed=False)
    s = inv_mod_curve_size(w)
    return int.from_bytes(res.raw[:32], "little", signed=False), s
