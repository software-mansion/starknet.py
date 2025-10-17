import hashlib
from typing import List

from starknet_py.constants import FIELD_PRIME

SMALL_THRESHOLD = 2**63
BIG_MARKER = 1 << 31  # MSB mask for the first u32 in the 8-limb case


def encode_felts_to_u32s(felts: List[int]) -> List[int]:
    """
    Encode each Felt into 32-bit words:
    - Small values < 2^63 get 2 words: [high_32_bits, low_32_bits] from the last 8 bytes
    - Large values >= 2^63 get 8 words: the full 32-byte big-endian split, with the
      MSB of the first word set as a marker (+2^255)

    Returns a flat list of u32 values.
    """
    unpacked_u32s = []
    for felt in felts:
        # Convert felt to 32-byte big-endian representation
        felt_as_be_bytes = felt.to_bytes(32, byteorder="big")

        if felt < SMALL_THRESHOLD:
            # Small: 2 limbs only, high-32 then low-32 of the last 8 bytes
            hi = int.from_bytes(felt_as_be_bytes[24:28], byteorder="big")
            lo = int.from_bytes(felt_as_be_bytes[28:32], byteorder="big")
            unpacked_u32s.append(hi)
            unpacked_u32s.append(lo)
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
    """
    assert len(hash_bytes) >= 32, "need at least 32 bytes to pack"
    # Interpret the 32-byte buffer as a little-endian integer and convert to Felt
    return int.from_bytes(hash_bytes[:32], byteorder="little") % FIELD_PRIME


def blake2s_to_felt(data: bytes) -> int:
    """
    Compute Blake2s-256 over data and return as a Felt (252-bit field element).
    """
    hash_bytes = hashlib.blake2s(data, digest_size=32).digest()
    return pack_256_le_to_felt(hash_bytes)


def encode_felt252_data_and_calc_blake_hash(felts: List[int]) -> int:
    """
    Encodes a list of Felt values into 32-bit words exactly as Cairo's
    encode_felt252_to_u32s hint does, then hashes the resulting byte stream
    with Blake2s-256 and returns the 256-bit digest as a 252-bit field element.
    """
    # 1) Unpack each Felt into 2 or 8 u32 limbs
    u32_words = encode_felts_to_u32s(felts)

    # 2) Serialize the u32 limbs into a little-endian byte stream
    byte_stream = b"".join(word.to_bytes(4, byteorder="little") for word in u32_words)

    # 3) Compute Blake2s-256 over the bytes and pack the result into a Felt
    return blake2s_to_felt(byte_stream)


def blake2s_hash_many(values: List[int]) -> int:
    """
    Hash multiple Felt values using the Cairo-compatible Blake2s encoding.
    This is the proper way to hash Felt values for Starknet.
    """
    return encode_felt252_data_and_calc_blake_hash(values)
