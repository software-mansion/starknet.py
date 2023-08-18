from dataclasses import dataclass
from typing import List, cast

from starknet_py.constants import DEFAULT_ENTRY_POINT_SELECTOR
from starknet_py.hash.address import compute_address
from starknet_py.hash.transaction import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_declare_v2_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_transaction_hash,
)
from starknet_py.hash.utils import message_signature, private_to_stark_key
from starknet_py.net.client_models import Hash
from starknet_py.net.models import AddressRepresentation, StarknetChainId, parse_address
from starknet_py.net.models.transaction import (
    AccountTransaction,
    Declare,
    DeclareV2,
    DeployAccount,
    Invoke,
)
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
        if isinstance(transaction, Declare):
            return self._sign_declare_transaction(transaction)
        if isinstance(transaction, DeclareV2):
            return self._sign_declare_v2_transaction(transaction)
        if isinstance(transaction, DeployAccount):
            return self._sign_deploy_account_transaction(transaction)
        return self._sign_transaction(cast(Invoke, transaction))

    def _sign_transaction(self, transaction: Invoke):
        tx_hash = compute_transaction_hash(
            tx_hash_prefix=TransactionHashPrefix.INVOKE,
            version=transaction.version,
            contract_address=self.address,
            entry_point_selector=DEFAULT_ENTRY_POINT_SELECTOR,
            calldata=transaction.calldata,
            max_fee=transaction.max_fee,
            chain_id=self.chain_id,
            additional_data=[transaction.nonce],
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]

    def _sign_declare_transaction(self, transaction: Declare) -> List[int]:
        tx_hash = compute_declare_transaction_hash(
            contract_class=transaction.contract_class,
            chain_id=self.chain_id,
            sender_address=self.address,
            max_fee=transaction.max_fee,
            version=transaction.version,
            nonce=transaction.nonce,
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]

    def _sign_declare_v2_transaction(self, transaction: DeclareV2) -> List[int]:
        tx_hash = compute_declare_v2_transaction_hash(
            contract_class=transaction.contract_class,
            compiled_class_hash=transaction.compiled_class_hash,
            chain_id=self.chain_id,
            sender_address=self.address,
            max_fee=transaction.max_fee,
            version=transaction.version,
            nonce=transaction.nonce,
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]

    def _sign_deploy_account_transaction(self, transaction: DeployAccount) -> List[int]:
        contract_address = compute_address(
            salt=transaction.contract_address_salt,
            class_hash=transaction.class_hash,
            constructor_calldata=transaction.constructor_calldata,
            deployer_address=0,
        )
        tx_hash = compute_deploy_account_transaction_hash(
            contract_address=contract_address,
            class_hash=transaction.class_hash,
            constructor_calldata=transaction.constructor_calldata,
            salt=transaction.contract_address_salt,
            max_fee=transaction.max_fee,
            version=transaction.version,
            chain_id=self.chain_id,
            nonce=transaction.nonce,
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        msg_hash = typed_data.message_hash(account_address)
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=msg_hash, priv_key=self.private_key)
        return [r, s]
