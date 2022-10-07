from dataclasses import dataclass
from typing import List

from starkware.crypto.signature.signature import (
    private_to_stark_key,
)
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_transaction_hash_common,
    TransactionHashPrefix,
    calculate_declare_transaction_hash,
    calculate_deploy_account_transaction_hash,
)

from starknet_py.net.models import (
    AddressRepresentation,
    StarknetChainId,
    Transaction,
    parse_address,
)
from starknet_py.net.models.transaction import DeployAccount, Declare, InvokeFunction
from starknet_py.net.signer.base_signer import BaseSigner
from starknet_py.utils.crypto.facade import message_signature
from starknet_py.utils.typed_data import TypedData as TypedDataDataclass
from starknet_py.net.models.typed_data import TypedData


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
        if isinstance(transaction, Declare):
            return self._sign_declare_transaction(transaction)
        if isinstance(transaction, DeployAccount):
            return self._sign_deploy_account_transaction(transaction)
        return self._sign_transaction(transaction)

    def _sign_transaction(self, transaction: InvokeFunction):
        tx_hash = calculate_transaction_hash_common(
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
        tx_hash = calculate_declare_transaction_hash(
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
        contract_address = calculate_contract_address_from_hash(
            salt=transaction.contract_address_salt,
            class_hash=transaction.class_hash,
            constructor_calldata=transaction.constructor_calldata,
            deployer_address=0,
        )
        tx_hash = calculate_deploy_account_transaction_hash(
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

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        typed_data_dataclass = TypedDataDataclass.from_dict(data=typed_data)
        msg_hash = typed_data_dataclass.message_hash(account_address)
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=msg_hash, priv_key=self.private_key)
        return [r, s]
