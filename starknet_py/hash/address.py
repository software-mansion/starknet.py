from typing import Sequence

from starknet_py.constants import CONTRACT_ADDRESS_PREFIX, L2_ADDRESS_UPPER_BOUND
from starknet_py.hash.utils import compute_hash_on_elements


def compute_address(
    *,
    class_hash: int,
    constructor_calldata: Sequence[int],
    salt: int,
    deployer_address: int = 0,
) -> int:
    """
    Computes the contract address in the StarkNet network - a unique identifier of the contract.

    :param class_hash: class hash of the contract
    :param constructor_calldata: calldata for the contract constructor
    :param salt: salt used to calculate contract address
    :param deployer_address: address of the deployer (if not provided default 0 is used)
    :return: Contract's address
    """

    constructor_calldata_hash = compute_hash_on_elements(data=constructor_calldata)
    raw_address = compute_hash_on_elements(
        data=[
            CONTRACT_ADDRESS_PREFIX,
            deployer_address,
            salt,
            class_hash,
            constructor_calldata_hash,
        ],
    )

    return raw_address % L2_ADDRESS_UPPER_BOUND
