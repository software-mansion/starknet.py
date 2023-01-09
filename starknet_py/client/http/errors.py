from typing import Optional


class ClientError(Exception):
    """
    Base class for all errors raised while attempting to communicate with StarkNet through Client.
    """

    def __init__(self, message: str, code: Optional[str] = None):
        self.code = code
        self.message = f"Client failed{f' with code {code}' if code is not None else ''}: {message}."
        super().__init__(self.message)
