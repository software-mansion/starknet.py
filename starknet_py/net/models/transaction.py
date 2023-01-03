from typing import Sequence, Union

from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    TransactionHashPrefix,
    calculate_transaction_hash_common,
)

# noinspection PyPep8Naming
from starkware.starknet.definitions.transaction_type import TransactionType as TT
from starkware.starknet.public.abi import get_selector_from_name

# noinspection PyPep8Naming
from starkware.starknet.services.api.gateway.transaction import Declare as DCL
from starkware.starknet.services.api.gateway.transaction import DeployAccount as DAC
from starkware.starknet.services.api.gateway.transaction import InvokeFunction as IF
from starkware.starknet.services.api.gateway.transaction import Transaction as T

from starknet_py.net.models.chains import StarknetChainId
from starknet_py.utils.crypto.facade import pedersen_hash
from starknet_py.utils.docs import as_our_module

Invoke = InvokeFunction = as_our_module(IF)
Transaction = as_our_module(T)
TransactionType = as_our_module(TT)
Declare = as_our_module(DCL)
DeployAccount = as_our_module(DAC)


def compute_invoke_hash(
    contract_address: int,
    entry_point_selector: Union[int, str],
    calldata: Sequence[int],
    chain_id: StarknetChainId,
    max_fee: int,
    version: int,
) -> int:
    # pylint: disable=too-many-arguments
    """
    Computes invocation hash.

    :param contract_address: int
    :param entry_point_selector: Union[int, str]
    :param calldata: Sequence[int]
    :param chain_id: StarknetChainId
    :param max_fee: Max fee
    :param version: Contract version
    :return: calculated hash
    """
    if isinstance(entry_point_selector, str):
        entry_point_selector = get_selector_from_name(entry_point_selector)

    return calculate_transaction_hash_common(
        tx_hash_prefix=TransactionHashPrefix.INVOKE,
        contract_address=contract_address,
        entry_point_selector=entry_point_selector,
        calldata=calldata,
        chain_id=chain_id.value,
        hash_function=pedersen_hash,
        additional_data=[],
        max_fee=max_fee,
        version=version,
    )
