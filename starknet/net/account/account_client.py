from dataclasses import dataclass
from typing import Dict, Optional, List

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.crypto.signature.signature import (
    private_to_stark_key,
    sign,
    get_random_private_key,
)
from starkware.starknet.definitions.transaction_type import TransactionType
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.gateway.transaction import InvokeFunction

from starknet.contract import Contract
from starknet.net import Client
from starknet.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet.utils.sync import add_sync_version
from starknet.utils.types import (
    AddressRepresentation,
    parse_address,
    Net,
)


@dataclass
class KeyPair:
    private_key: int
    public_key: int

    @staticmethod
    def from_private_key(key: int) -> "KeyPair":
        return KeyPair(private_key=key, public_key=private_to_stark_key(key))


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


@add_sync_version
class AccountClient(Client):
    def __init__(
        self,
        address: AddressRepresentation,
        key_pair: KeyPair,
        net: Net,
        *args,
        **kwargs,
    ):
        super().__init__(net, *args, **kwargs)
        self.address = parse_address(address)
        self._key_pair = key_pair

    @property
    def private_key(self) -> int:
        return self._key_pair.private_key

    async def add_transaction(
        self,
        tx: InvokeFunction,
        token: Optional[str] = None,
    ) -> Dict[str, int]:
        if tx.tx_type == TransactionType.DEPLOY:
            return await super().add_transaction(tx, token)

        if tx.signature:
            raise TypeError(
                f"Adding signatures to a signer tx currently isn't supported"
            )

        result = await super().call_contract(
            InvokeFunction(
                contract_address=self.address,
                entry_point_selector=get_selector_from_name("get_nonce"),
                calldata=[],
                signature=[],
            )
        )
        nonce = result[0]

        msg_hash = hash_message(
            account=self.address,
            to=tx.contract_address,
            selector=tx.entry_point_selector,
            calldata=tx.calldata,
            nonce=nonce,
        )

        r, s = sign(msg_hash=msg_hash, priv_key=self.private_key)

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

    @staticmethod
    async def create_account(net: Net, pk: Optional[int] = None) -> "AccountClient":
        if not pk:
            pk = get_random_private_key()

        key_pair = KeyPair.from_private_key(pk)

        client = Client(net=net)
        account_contract = await Contract.deploy(
            client=client,
            constructor_args=[key_pair.public_key],
            compiled_contract=COMPILED_ACCOUNT_CONTRACT,
        )

        return AccountClient(
            net=net,
            address=account_contract.address,
            key_pair=key_pair,
        )
