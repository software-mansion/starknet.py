from typing import Optional


class WebsocketClientError(Exception):
    """
    Base class for all errors raised while attempting to communicate with Starknet through WebsocketClient.
    """

    def __init__(
        self, message: str, code: Optional[str] = None, data: Optional[str] = None
    ):
        self.code = code
        self.data = data
        self.message = (
            f"WebsocketClient failed{f' with code {code}' if code is not None else ''}. "
            f"Message: {message}.{f' Data: {data}' if data is not None else ''}"
        )

        super().__init__(self.message)
