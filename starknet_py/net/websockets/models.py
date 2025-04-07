"""
Dataclasses representing responses from Starknet Websocket RPC API.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

from starknet_py.net.client_models import (
    BlockHeader,
    EmittedEvent,
    TransactionStatusResponse,
)
from starknet_py.net.models import (
    DeclareV1,
    DeclareV2,
    DeclareV3,
    DeployAccountV1,
    DeployAccountV3,
    InvokeV1,
    InvokeV3,
)

T = TypeVar("T")


@dataclass
class Notification(Generic[T]):
    """
    Base class for notification.
    """

    subscription_id: str
    result: T


@dataclass
class NewHeadsNotification(Notification[BlockHeader]):
    """
    Notification to the client of a new block header.
    """


@dataclass
class NewEventsNotification(Notification[EmittedEvent]):
    """
    Notification to the client of a new event.
    """


@dataclass
class NewTransactionStatus:
    """
    New transaction status.
    """

    transaction_hash: int
    status: TransactionStatusResponse


@dataclass
class TransactionStatusNotification(Notification[NewTransactionStatus]):
    """
    Notification to the client of a new transaction status.
    """


Transaction = Union[
    DeclareV1,
    DeclareV2,
    DeclareV3,
    DeployAccountV1,
    DeployAccountV3,
    InvokeV1,
    InvokeV3,
]


@dataclass
class PendingTransactionsNotification(Notification[Union[int, Transaction]]):
    """
    Notification to the client of a new pending transaction.
    """


@dataclass
class ReorgData:
    """
    Data about reorganized blocks, starting and ending block number and hash.
    """

    starting_block_hash: int
    starting_block_number: int
    ending_block_hash: int
    ending_block_number: int


@dataclass
class ReorgNotification(Notification[ReorgData]):
    """
    Notification of a reorganization of the chain.
    """
