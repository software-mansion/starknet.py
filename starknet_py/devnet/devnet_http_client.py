from typing import Optional

from starknet_py.net.http_client import HttpMethod, RpcHttpClient


class DevnetRpcHttpClient(RpcHttpClient):
    async def call(self, method_name: str, params: Optional[dict] = None):
        payload = {
            "jsonrpc": "2.0",
            "method": f"devnet_{method_name}",
            "id": 1,
            "params": params if params else [],
        }

        result = await self.request(
            http_method=HttpMethod.POST, address=self.url, payload=payload
        )

        if "result" not in result:
            self.handle_rpc_error(result)
        return result["result"]
