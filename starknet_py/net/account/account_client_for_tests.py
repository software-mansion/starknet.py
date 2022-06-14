from starkware.starknet.public.abi import (
    get_selector_from_name,
)
from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet_py.net import AccountClient
from starknet_py.net.models import InvokeFunction
from starknet_py.utils.data_transformer import DataTransformer
from starknet_py.utils.sync import add_sync_methods
from starknet_py.utils.crypto.facade import (
    message_signature,
    hash_multicall,
    MultiCall,
    Call,
)
from starknet_py.net.models.address import parse_address


@add_sync_methods
class AccountClientForTests(AccountClient):
    """
    Extends the functionality of :obj:`AccountClient <starknet_py.net.Client>`, it is used for tests on devnet
    """

    async def _prepare_invoke_function(self, tx: InvokeFunction) -> InvokeFunction:
        nonce = await self._get_nonce()

        calldata_py = [
            [
                {
                    "to": tx.contract_address,
                    "selector": tx.entry_point_selector,
                    "data_offset": 0,
                    "data_len": len(tx.calldata),
                }
            ],
            tx.calldata,
            nonce,
        ]

        code = await self.get_code(contract_address=parse_address(self.address))
        abi = code["abi"]
        identifier_manager = identifier_manager_from_abi(abi)
        [execute_abi] = [a for a in abi if a["name"] == "__execute__"]

        payload_transformer = DataTransformer(
            abi=execute_abi, identifier_manager=identifier_manager
        )

        wrapped_calldata, _ = payload_transformer.from_python(*calldata_py)

        multicall = MultiCall(
            account=self.address,
            calls=[
                Call(
                    tx.contract_address,
                    tx.entry_point_selector,
                    tx.calldata,
                )
            ],
            nonce=nonce,
            max_fee=tx.max_fee,
            version=0,
        )

        # pylint: disable=invalid-name
        r, s = message_signature(
            msg_hash=hash_multicall(multicall), priv_key=self.private_key
        )

        return InvokeFunction(
            entry_point_selector=get_selector_from_name("__execute__"),
            calldata=wrapped_calldata,
            contract_address=self.address,
            signature=[r, s],
            max_fee=tx.max_fee,
            version=0,
        )
