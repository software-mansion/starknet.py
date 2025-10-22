"""
This module's Blake2s felt encoding and hashing logic is based on StarkWare's
sequencer implementation:
https://github.com/starkware-libs/sequencer/blob/b29c0e8c61f7b2340209e256cf87dfe9f2c811aa/crates/blake2s/src/lib.rs
"""

import hashlib
from typing import List

from starknet_py.constants import FIELD_PRIME

SMALL_THRESHOLD = 2**63
BIG_MARKER = 1 << 31  # MSB mask for the first u32 in the 8-limb case


def encode_felts_to_u32s(felts: List[int]) -> List[int]:
    """
    Encode each Felt into 32-bit words following Cairo's encoding scheme.

    Small values (< 2^63) are encoded as 2 words: [high_32_bits, low_32_bits] from the last 8 bytes.
    Large values (>= 2^63) are encoded as 8 words: the full 32-byte big-endian split,
    with the MSB of the first word set as a marker (+2^255).

    :param felts: List of Felt values to encode
    :return: Flat list of u32 values
    """
    unpacked_u32s = []
    for felt in felts:
        # Convert felt to 32-byte big-endian representation
        felt_as_be_bytes = felt.to_bytes(32, byteorder="big")

        if felt < SMALL_THRESHOLD:
            # Small: 2 limbs only, high-32 then low-32 of the last 8 bytes
            high = int.from_bytes(felt_as_be_bytes[24:28], byteorder="big")
            low = int.from_bytes(felt_as_be_bytes[28:32], byteorder="big")
            unpacked_u32s.append(high)
            unpacked_u32s.append(low)
        else:
            # Big: 8 limbs, big-endian order
            start = len(unpacked_u32s)
            for i in range(0, 32, 4):
                limb = int.from_bytes(felt_as_be_bytes[i : i + 4], byteorder="big")
                unpacked_u32s.append(limb)
            # Set the MSB of the very first limb as the Cairo hint does with "+ 2**255"
            unpacked_u32s[start] |= BIG_MARKER

    return unpacked_u32s


def pack_256_le_to_felt(hash_bytes: bytes) -> int:
    """
    Packs the first 32 bytes (256 bits) of hash_bytes into a Felt (252 bits).
    Interprets the bytes as a Felt (252 bits)

    :param hash_bytes: Hash bytes (at least 32 bytes required)
    :return: Felt value (252-bit field element)
    """
    assert len(hash_bytes) >= 32, "need at least 32 bytes to pack"
    # Interpret the 32-byte buffer as a little-endian integer and convert to Felt
    return int.from_bytes(hash_bytes[:32], byteorder="little") % FIELD_PRIME


def blake2s_to_felt(data: bytes) -> int:
    """
    Compute Blake2s-256 hash over data and return as a Felt.

    :param data: Input data to hash
    :return: Blake2s-256 hash as a 252-bit field element
    """
    hash_bytes = hashlib.blake2s(data, digest_size=32).digest()
    return pack_256_le_to_felt(hash_bytes)


def encode_felt252_data_and_calc_blake_hash(felts: List[int]) -> int:
    """
    Encodes Felt values using Cairo's encoding scheme and computes Blake2s hash.

    This function matches Cairo's encode_felt252_to_u32s hint behavior. It encodes
    each Felt into 32-bit words, serializes them as little-endian bytes, then
    computes Blake2s-256 hash over the byte stream.

    :param felts: List of Felt values to encode and hash
    :return: Blake2s-256 hash as a 252-bit field element
    """
    # Unpack each Felt into 2 or 8 u32 limbs
    u32_words = encode_felts_to_u32s(felts)

    # Serialize the u32 limbs into a little-endian byte stream
    byte_stream = b"".join(word.to_bytes(4, byteorder="little") for word in u32_words)

    # Compute Blake2s-256 over the bytes and pack the result into a Felt
    return blake2s_to_felt(byte_stream)


def blake2s_hash_many(values: List[int]) -> int:
    """
    Hash multiple Felt values using Cairo-compatible Blake2s encoding.

    This is the recommended way to hash Felt values for Starknet when using
    Blake2s as the hash method.

    :param values: List of Felt values to hash
    :return: Blake2s-256 hash as a 252-bit field element
    """
    return encode_felt252_data_and_calc_blake_hash(values)
