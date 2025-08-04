from typing import List

from eth_keys import keys  # pyright: ignore[reportPrivateImportUsage]
from eth_keys.datatypes import Signature

from starknet_py.net.client_models import Hash
from starknet_py.net.models import AccountTransaction
from starknet_py.net.models.chains import ChainId
from starknet_py.net.signer.base_signer import BaseSigner
from starknet_py.serialization import Uint256Serializer
from starknet_py.utils.typed_data import TypedData


class EthSigner(BaseSigner):
    def __init__(
        self,
        private_key: Hash,
        chain_id: ChainId,
    ):
        if isinstance(private_key, str):
            private_key = int(private_key, 0)

        private_key_bytes = private_key.to_bytes(32, byteorder="big")
        self._private_key = keys.PrivateKey(private_key_bytes)
        self.chain_id = chain_id

    @property
    def public_key(self) -> int:
        return int.from_bytes(self._private_key.public_key.to_bytes(), byteorder="big")

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        msg_hash = typed_data.message_hash(account_address)
        signature = self._private_key.sign_msg_hash(
            msg_hash.to_bytes(32, byteorder="big")
        )

        return _serialize_signature(signature)

    def sign_transaction(self, transaction: AccountTransaction) -> List[int]:
        tx_hash = transaction.calculate_hash(self.chain_id)
        signature = self._private_key.sign_msg_hash(
            tx_hash.to_bytes(32, byteorder="big")
        )

        return _serialize_signature(signature)


# eth signature components `r` and `s` are 32 bytes each, so they are stored as u256
def _serialize_signature(signature: Signature) -> List[int]:
    serializer = Uint256Serializer()
    return (
        serializer.serialize(signature.r)
        + serializer.serialize(signature.s)
        + [signature.v]
    )
