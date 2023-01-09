from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence, Union

from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    TransactionHashPrefix,
    calculate_transaction_hash_common,
)

# noinspection PyPep8Naming
from starkware.starknet.public.abi import get_selector_from_name

# noinspection PyPep8Naming
from starkware.starknet.services.api.gateway.transaction import Declare as DCL
from starkware.starknet.services.api.gateway.transaction import DeployAccount as DAC
from starkware.starknet.services.api.gateway.transaction import InvokeFunction as IF
from starkware.starknet.services.api.gateway.transaction import Transaction as T

from starknet_py.client.models.chains import StarknetChainId
from starknet_py.client.models.event import Event
from starknet_py.client.models.message import L1toL2Message, L2toL1Message
from starknet_py.utils.crypto.facade import pedersen_hash
from starknet_py.utils.docs import as_our_module

StarknetTransaction = as_our_module(T)
Invoke = InvokeFunction = as_our_module(IF)
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


@dataclass
class Transaction(ABC):
    """
    Dataclass representing common attributes of all transactions
    """

    hash: int
    signature: List[int]
    max_fee: int
    version: int

    def __post_init__(self):
        if self.__class__ == Transaction:
            raise TypeError("Cannot instantiate abstract Transaction class.")


@dataclass
class InvokeTransaction(Transaction):
    """
    Dataclass representing invoke transaction
    """

    contract_address: int
    calldata: List[int]
    # This field is always None for transactions with version = 1
    entry_point_selector: Optional[int] = None
    nonce: Optional[int] = None


@dataclass
class DeclareTransaction(Transaction):
    """
    Dataclass representing declare transaction
    """

    class_hash: int
    sender_address: int
    nonce: Optional[int] = None


@dataclass
class DeployTransaction(Transaction):
    """
    Dataclass representing deploy transaction
    """

    contract_address: Optional[int]
    constructor_calldata: List[int]
    class_hash: int


@dataclass
class DeployAccountTransaction(Transaction):
    """
    Dataclass representing deploy account transaction
    """

    contract_address_salt: int
    class_hash: int
    constructor_calldata: List[int]
    nonce: int


@dataclass
class L1HandlerTransaction(Transaction):
    """
    Dataclass representing l1 handler transaction
    """

    contract_address: int
    calldata: List[int]
    entry_point_selector: int
    nonce: Optional[int] = None


class TransactionStatus(Enum):
    """
    Enum representing transaction statuses
    """

    NOT_RECEIVED = "NOT_RECEIVED"
    RECEIVED = "RECEIVED"
    PENDING = "PENDING"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    REJECTED = "REJECTED"


@dataclass
class TransactionReceipt:
    """
    Dataclass representing details of sent transaction
    """

    # pylint: disable=too-many-instance-attributes

    hash: int
    status: TransactionStatus
    block_number: Optional[int] = None
    block_hash: Optional[int] = None
    actual_fee: int = 0
    rejection_reason: Optional[str] = None

    events: List[Event] = field(default_factory=list)
    l2_to_l1_messages: List[L2toL1Message] = field(default_factory=list)
    l1_to_l2_consumed_message: Optional[L1toL2Message] = None


class TransactionType(Enum):
    """
    Enum representing transaction types
    """

    INVOKE = "INVOKE"
    DEPLOY = "DEPLOY"
    DECLARE = "DECLARE"
    DEPLOY_ACCOUNT = "DEPLOY_ACCOUNT"
    L1_HANDLER = "L1_HANDLER"
