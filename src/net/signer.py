from dataclasses import dataclass
from typing import Dict, Optional, List

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.starknet.definitions.transaction_type import TransactionType
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.gateway.transaction import InvokeFunction
from starkware.crypto.signature.signature import private_to_stark_key, sign
from src.net import Client
from src.types import AddressRepresentation, parse_address


@dataclass
class KeyPair:
    private_key: int
    public_key: int


def hash_message(
    account: int, to: int, selector: int, calldata: List[int], nonce: int
) -> int:
    return compute_hash_on_elements(
        [
            account,
            to,
            selector,
            compute_hash_on_elements(calldata),
            nonce,
        ]
    )


class Signer(Client):
    def __init__(
        self, address: AddressRepresentation, key_pair: KeyPair, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.address = parse_address(address)
        self.key_pair = key_pair

    async def add_transaction(
        self,
        tx: InvokeFunction,
        token: Optional[str] = None,
    ) -> Dict[str, int]:
        if tx.tx_type == TransactionType.DEPLOY:
            return await super().add_transaction(tx, token)

        result = await super().call_contract(
            InvokeFunction(
                contract_address=self.address,
                entry_point_selector=get_selector_from_name("get_nonce"),
                calldata=[],
                signature=[],
            )
        )
        nonce = int(result["result"][0], 16)

        msg_hash = hash_message(
            account=self.address,
            to=tx.contract_address,
            selector=tx.entry_point_selector,
            calldata=tx.calldata,
            nonce=nonce,
        )

        stark_key = private_to_stark_key(self.key_pair.private_key)
        r, s = sign(msg_hash=msg_hash, priv_key=stark_key)

        return await super().add_transaction(
            InvokeFunction(
                entry_point_selector=get_selector_from_name("execute"),
                calldata=[
                    tx.contract_address,
                    tx.entry_point_selector,
                    len(tx.calldata),
                    *tx.calldata,
                    nonce,
                ],
                contract_address=self.address,
                signature=[r, s],
            )
        )
