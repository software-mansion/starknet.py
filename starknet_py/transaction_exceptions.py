from typing import Optional


class TransactionFailedException(Exception):
    """
    Base exception for transaction failure
    """

    def __init__(self, tx_failure_reason: Optional[str] = None):
        self.transaction_failure_reason = tx_failure_reason or "Unknown starknet error."
        super().__init__(self.transaction_failure_reason)

    def __str__(self):
        return f"Transaction failed with following starknet error: {self.transaction_failure_reason}."


class TransactionRejectedException(TransactionFailedException):
    """
    Exception for transactions rejected by starknet
    """

    def __init__(self, transaction_rejection_reason: str):
        super().__init__(transaction_rejection_reason)

    def __str__(self):
        return f"Transaction was rejected with following starknet error: {self.transaction_failure_reason}."


class TransactionNotReceivedException(TransactionFailedException):
    """
    Exception for transactions not received on starknet
    """

    def __init__(self):
        super().__init__("Transaction not received")

    def __str__(self):
        return "Transaction was not received on starknet."
