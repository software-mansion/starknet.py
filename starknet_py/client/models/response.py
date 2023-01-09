from dataclasses import dataclass
from typing import Optional

from starknet_py.client.models.transaction import TransactionStatus


@dataclass
class SentTransactionResponse:
    """
    Dataclass representing a result of sending a transaction to starknet
    """

    transaction_hash: int
    code: Optional[str] = None


@dataclass
class DeclareTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of declaring a contract on starknet
    """

    class_hash: int = 0


@dataclass
class DeployAccountTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of deploying an account contract to starknet
    """

    address: int = 0


@dataclass
class TransactionStatusResponse:
    block_hash: Optional[int]
    transaction_status: TransactionStatus
