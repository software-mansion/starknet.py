import warnings
from dataclasses import dataclass
from typing import Dict, List, Union

from starkware.crypto.signature.signature import private_to_stark_key

from starknet_py.net.models import (
    AddressRepresentation,
    StarknetChainId,
    Transaction,
    compute_address,
    parse_address,
)
from starknet_py.net.models.transaction import (
    Declare,
    DeployAccount,
    Invoke,
    TransactionType,
)
from starknet_py.net.signer.base_signer import BaseSigner
from starknet_py.utils.crypto.facade import message_signature
from starknet_py.utils.crypto.transaction_hash import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_transaction_hash,
)
from starknet_py.utils.typed_data import TypedData


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
        if transaction.tx_type() == TransactionType.DECLARE:
            return self._sign_declare_transaction(transaction)
        if isinstance(transaction, DeployAccount):
            return self._sign_deploy_account_transaction(transaction)
        return self._sign_transaction(transaction)

    def _sign_transaction(self, transaction: Invoke):
        tx_hash = compute_transaction_hash(
            tx_hash_prefix=TransactionHashPrefix.INVOKE,
            version=transaction.version,
            contract_address=self.address,
            entry_point_selector=0
            if transaction.version == 1
            else transaction.entry_point_selector,
            calldata=transaction.calldata,
            max_fee=transaction.max_fee,
            chain_id=self.chain_id.value,
            additional_data=[transaction.nonce] if transaction.version == 1 else [],
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]

    def _sign_declare_transaction(self, transaction: Declare) -> List[int]:
        tx_hash = compute_declare_transaction_hash(
            contract_class=transaction.contract_class,
            chain_id=self.chain_id.value,
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
            chain_id=self.chain_id.value,
            nonce=transaction.nonce,
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]

    def sign_message(
        self, typed_data: Union[Dict, TypedData], account_address: int
    ) -> List[int]:
        if isinstance(typed_data, dict):
            warnings.warn(
                "Argument typed_data as dict has been deprecated. Use starknet_py.utils.TypedData dataclass instead.",
                category=DeprecationWarning,
            )

        typed_data_dataclass = (
            # Typechecker expects typed_data to be a TypedDict but typing of sign_message changed due to depreaction
            TypedData.from_dict(data=typed_data)  # pyright: ignore
            if isinstance(typed_data, dict)
            else typed_data
        )
        msg_hash = typed_data_dataclass.message_hash(account_address)
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=msg_hash, priv_key=self.private_key)
        return [r, s]
