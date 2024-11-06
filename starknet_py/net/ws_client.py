import json
from typing import Any, Dict, Optional, Union, cast

from websockets.asyncio.client import ClientConnection, connect

from starknet_py.net.http_client import RpcHttpClient


class WSClient:
    """
    Base class for WebSocket clients.
    """

    def __init__(self, node_url: str):
        """
        :param node_url: URL of the node providing the WebSocket API.
        """
        self.node_url: str = node_url
        self.connection: Union[None, ClientConnection] = None

    async def connect(self):
        """Establishes the WebSocket connection."""
        self.connection = await connect(self.node_url)

    async def disconnect(self):
        """Closes the WebSocket connection."""
        assert self.connection is not None
        await self.connection.close()

    async def send_raw(
        self,
        payload: Optional[Dict[str, Any]] = None,
    ):
        assert self.connection is not None
        await self.connection.send(json.dumps(payload))
        data = await self.connection.recv()

        return data


class RpcWSClient(WSClient):
    """
    WebSocket client for the RPC API.
    """

    async def send(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "id": 0,
            "jsonrpc": "2.0",
            "method": method,
            "params": params if params else [],
        }

        data = await self.send_raw(payload)
        data = cast(Dict, json.loads(data))

        if "result" not in data:
            RpcHttpClient.handle_rpc_error(data)

        return data
