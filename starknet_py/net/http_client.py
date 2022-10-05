from abc import abstractmethod, ABC
from enum import Enum
from typing import Optional

from aiohttp import ClientSession, ClientResponse

from starknet_py.net.client_errors import ClientError


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class HttpClient(ABC):
    def __init__(self, url, session: Optional[ClientSession] = None):
        self.url = url
        self.session = session

    async def request(
        self,
        address: str,
        http_method: HttpMethod,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
    ):
        kwargs = {
            "address": address,
            "http_method": http_method,
            "params": params,
            "payload": payload,
        }
        if self.session:
            return await self._make_request(session=self.session, **kwargs)

        async with ClientSession() as session:
            return await self._make_request(session=session, **kwargs)

    async def _make_request(
        self,
        session: ClientSession,
        address: str,
        http_method: HttpMethod,
        params: dict,
        payload: dict,
    ) -> dict:
        # pylint: disable=too-many-arguments
        async with session.request(
            method=http_method.value, url=address, params=params, json=payload
        ) as request:
            await self.handle_request_error(request)
            return await request.json(content_type=None)

    @abstractmethod
    async def handle_request_error(self, request: ClientResponse):
        """
        Handle an errors returned by make_request
        """


class GatewayHttpClient(HttpClient):
    async def call(self, method_name: str, params: Optional[dict] = None) -> dict:
        return await self.request(
            http_method=HttpMethod.GET, address=self.address(method_name), params=params
        )

    async def post(
        self, method_name: str, payload: dict, params: Optional[dict] = None
    ) -> dict:
        return await self.request(
            http_method=HttpMethod.POST,
            address=self.address(method_name),
            payload=payload,
            params=params,
        )

    def address(self, method_name):
        return f"{self.url}/{method_name}"

    async def handle_request_error(self, request: ClientResponse):
        await basic_error_handle(request)


class RpcHttpClient(HttpClient):
    async def call(self, method_name: str, params: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": f"starknet_{method_name}",
            "params": params,
            "id": 0,
        }

        result = await self.request(
            http_method=HttpMethod.POST, address=self.url, payload=payload
        )

        if "result" not in result:
            self.handle_rpc_error(result)
        return result["result"]

    @staticmethod
    def handle_rpc_error(result: dict):
        if "error" not in result:
            raise ServerError(body=result)
        raise ClientError(
            code=result["error"]["code"], message=result["error"]["message"]
        )

    async def handle_request_error(self, request: ClientResponse):
        await basic_error_handle(request)


async def basic_error_handle(request: ClientResponse):
    if request.status >= 300:
        raise ClientError(code=str(request.status), message=await request.text())


class ServerError(Exception):
    def __init__(self, body: dict):
        self.message = "Rpc request failed"
        self.body = body
        super().__init__(self.message)
