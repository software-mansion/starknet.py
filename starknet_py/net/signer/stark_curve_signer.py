from dataclasses import dataclass
from typing import List

from starknet_py.hash.utils import message_signature, private_to_stark_key
from starknet_py.net.client_models import Hash
from starknet_py.net.models import AddressRepresentation, StarknetChainId, parse_address
from starknet_py.net.models.transaction import AccountTransaction
from starknet_py.net.signer.base_signer import BaseSigner
from starknet_py.utils.typed_data import TypedData


@dataclass
class KeyPair:
    private_key: int
    public_key: int

    def __init__(self, private_key: Hash, public_key: Hash):
        if isinstance(private_key, str):
            self.private_key = int(private_key, 0)
        else:
            self.private_key = private_key

        if isinstance(public_key, str):
            self.public_key = int(public_key, 0)
        else:
            self.public_key = public_key

    @staticmethod
    def from_private_key(key: Hash) -> "KeyPair":
        if isinstance(key, str):
            key = int(key, 0)
        return KeyPair(private_key=key, public_key=private_to_stark_key(key))


class StarkCurveSigner(BaseSigner):
    def __init__(
        self,
        account_address: AddressRepresentation,
        key_pair: KeyPair,
        chain_id: StarknetChainId,
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
