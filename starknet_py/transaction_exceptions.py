from typing import Optional


class TransactionFailedError(Exception):
    """
    Base exception for transaction failure
    """

    def __init__(
        self,
        message: Optional[str] = None,
    ):
        if message is None:
            message = "Unknown starknet error"
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Transaction failed with following starknet error: {self.message}."


class TransactionRejectedError(TransactionFailedError):
    """
    Exception for transactions rejected by starknet
    """

    def __str__(self):
        return (
            "Transaction was rejected with following starknet error: "
            f"{self.message}."
        )


class TransactionNotReceivedError(TransactionFailedError):
    """
    Exception for transactions not received on starknet
    """

    def __init__(self):
        super().__init__(message="Transaction not received")

    def __str__(self):
        return "Transaction was not received on starknet"
