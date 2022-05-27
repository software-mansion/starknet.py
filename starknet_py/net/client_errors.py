from typing import Optional, Union


class ClientError(Exception):
    def __init__(self, message: str, code: Optional[str] = None):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Client failed{f' with code {self.code}' if self.code is not None else ''}: {self.message}"


class ContractNotFoundError(ClientError):
    def __int__(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ):
        if block_hash is None and block_number is None:
            raise ValueError("One of block hash or number must be provided")

        identifier = block_hash or block_number
        self.identifier = str(identifier) if isinstance(identifier, int) else identifier

        super().__init__(message=f"No contract found for identifier: {self.identifier}")

    def __str__(self):
        return self.message
