from typing import Union, Sequence

from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    BlockIdentifier,
)


from starknet_py.utils.docs import as_our_module

AddressRepresentation = Union[int, str]
Address = int


def parse_address(value: AddressRepresentation) -> Address:
    if isinstance(value, int):
        return value

    try:
        return int(value, 16)
    except TypeError as t_err:
        raise TypeError("Invalid address format.") from t_err


def compute_address(
    *,
    class_hash: int,
    constructor_calldata: Sequence[int],
    salt: int,
    deployer_address: int = 0,
) -> int:
    """
    Computes contract's address.

    :param class_hash: class hash of the contract
    :param constructor_calldata: calldata for the contract constructor
    :param salt: salt used to calculate contract address
    :param deployer_address: address of the deployer (if not provided default 0 is used)
    :return: Contract's address
    """

    return calculate_contract_address_from_hash(
        class_hash=class_hash,
        constructor_calldata=constructor_calldata,
        salt=salt,
        deployer_address=deployer_address,
    )


BlockIdentifier = as_our_module(BlockIdentifier)
