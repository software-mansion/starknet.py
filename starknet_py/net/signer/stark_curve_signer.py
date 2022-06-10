from dataclasses import dataclass
from typing import List

from starkware.crypto.signature.signature import (
    private_to_stark_key,
)
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_transaction_hash_common,
    TransactionHashPrefix,
)

from starknet_py.net.models import (
    AddressRepresentation,
    StarknetChainId,
    Transaction,
    parse_address,
)
from starknet_py.net.signer.base_signer import BaseSigner
from starknet_py.utils.crypto.facade import message_signature


@dataclass
class KeyPair:
    private_key: int
    public_key: int

    @staticmethod
    def from_private_key(key: int) -> "KeyPair":
        return KeyPair(private_key=key, public_key=private_to_stark_key(key))


class StarkCurveSigner(BaseSigner):
    def __init__(
        self,
        account_address: AddressRepresentation,
        key_pair: KeyPair,
        chain_id: StarknetChainId,
    ):
        self.address = parse_address(account_address)
        self.key_pair = key_pair
        self.chain_id = chain_id

    @property
    def private_key(self) -> int:
        return self.key_pair.private_key

    @property
    def public_key(self) -> int:
        return self.key_pair.public_key

    def sign_transaction(
        self,
        transaction: Transaction,
    ) -> List[int]:
        tx_hash = calculate_transaction_hash_common(
            tx_hash_prefix=TransactionHashPrefix.INVOKE,
            version=transaction.version,
            contract_address=self.address,
            entry_point_selector=transaction.entry_point_selector,
            calldata=transaction.calldata,
            max_fee=transaction.max_fee,
            chain_id=self.chain_id.value,
            additional_data=[],
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]
