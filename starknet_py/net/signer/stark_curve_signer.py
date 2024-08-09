from typing import List

from starknet_py.hash.utils import message_signature
from starknet_py.net.models import AddressRepresentation, parse_address
from starknet_py.net.models.chains import ChainId
from starknet_py.net.models.transaction import AccountTransaction
from starknet_py.net.signer.base_signer import BaseSigner
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.utils.typed_data import TypedData


class StarkCurveSigner(BaseSigner):
    def __init__(
        self,
        account_address: AddressRepresentation,
        key_pair: KeyPair,
        chain_id: ChainId,
    ):
        """
        :param account_address: Address of the account contract.
        :param key_pair: Key pair of the account contract.
        :param chain_id: ChainId of the chain.
        """
        self.address = parse_address(account_address)
        self.key_pair = key_pair
        self.chain_id = chain_id

    @property
    def private_key(self) -> int:
        """Private key of the signer."""
        return self.key_pair.private_key

    @property
    def public_key(self) -> int:
        return self.key_pair.public_key

    def sign_transaction(
        self,
        transaction: AccountTransaction,
    ) -> List[int]:
        tx_hash = transaction.calculate_hash(self.chain_id)
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        msg_hash = typed_data.message_hash(account_address)
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=msg_hash, priv_key=self.private_key)
        return [r, s]
