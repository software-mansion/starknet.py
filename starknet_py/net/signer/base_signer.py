from abc import ABC, abstractmethod
from typing import List

from starknet_py.net.models.transaction import Transaction
from starknet_py.net.models.typed_data import TypedData


class BaseSigner(ABC):
    """
    Base class for transaction signer. Implement methods from this ABC to use a custom signer in AccountClient
    """

    @property
    @abstractmethod
    def public_key(self) -> int:
        """
        Public key of the signer

        :return: public key
        """

    @abstractmethod
    def sign_transaction(self, transaction: Transaction) -> List[int]:
        """
        Sign execute transaction and return a signature

        :param transaction: Execute transaction to sign
        :return: transaction signature
        """

    @abstractmethod
    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        """
        Sign an TypedData TypedDict for off-chain usage with the starknet private key and return the signature
        This adds a message prefix, so it can't be interchanged with transactions

        :param typed_data: TypedData TypedDict to be signed
        :param account_address: account address
        :return: the signature of the JSON object
        """
