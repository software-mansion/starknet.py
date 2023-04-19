from abc import ABC, abstractmethod
from typing import List

from starknet_py.net.models.transaction import AccountTransaction
from starknet_py.utils.typed_data import TypedData


class BaseSigner(ABC):
    """
    Base class for transaction signer. Implement methods from this ABC to use a custom signer in Account.
    """

    @property
    @abstractmethod
    def public_key(self) -> int:
        """
        Public key of the signer.

        :return: public key
        """

    @abstractmethod
    def sign_transaction(self, transaction: AccountTransaction) -> List[int]:
        """
        Sign execute transaction and return a signature

        :param transaction: Execute transaction to sign
        :return: transaction signature
        """

    @abstractmethod
    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        """
        Sign TypedData object for off-chain usage with the Starknet private key and return the signature.
        This adds a message prefix, so it can't be interchanged with transactions.

        :param typed_data: TypedData to be signed.
        :param account_address: account address.
        :return: the signature of the JSON object.
        """
