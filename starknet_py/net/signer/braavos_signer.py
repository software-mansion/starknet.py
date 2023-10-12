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
from starknet_py.hash.utils import compute_hash_on_elements, message_signature
from starknet_py.net.models import (
    AccountTransaction,
    AddressRepresentation,
    Declare,
    DeclareV2,
    DeployAccount,
    Invoke,
    StarknetChainId,
    parse_address,
)
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.utils.typed_data import TypedData


class BraavosSigner(BaseSigner):
    def __init__(
        self,
        account_address: AddressRepresentation,
        key_pair: KeyPair,
        chain_id: StarknetChainId,
        current_account_implementation_class_hash: int = 0x0105C0CF7AADB6605C9538199797920884694B5CE84FC68F92C832B0C9F57AD9,
    ):
        """
        :param account_address: Address of the account contract.
        :param key_pair: Key pair of the account contract.
        :param current_account_implementation_class_hash: Current implementation of Braavos account.
        :param chain_id: ChainId of the chain.
        """
        self.address = parse_address(account_address)
        self.key_pair = key_pair
        # Current Braavos account implementation class hash
        self.actual_impl = current_account_implementation_class_hash
        self.chain_id = chain_id
        # Hardware signer - in our situation seven zeros
        self._hw_signer = [0, 0, 0, 0, 0, 0, 0]

    @property
    def private_key(self):
        """Private key of the signer."""
        return self.key_pair.private_key

    @property
    def public_key(self) -> int:
        """Public key of the signer."""
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
        r, s = message_signature(
            msg_hash=compute_hash_on_elements(
                [tx_hash, self.actual_impl, *self._hw_signer]
            ),
            priv_key=self.private_key,
        )
        return [r, s, self.actual_impl, *self._hw_signer]

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        pass