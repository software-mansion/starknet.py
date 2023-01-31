from abc import ABC, abstractmethod
from typing import Dict, List, Union

from starknet_py.net.models.transaction import Transaction
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
    def sign_transaction(self, transaction: Transaction) -> List[int]:
        """
        Sign execute transaction and return a signature

        :param transaction: Execute transaction to sign
        :return: transaction signature
        """

    @abstractmethod
    def sign_message(
        self, typed_data: Union[Dict, TypedData], account_address: int
    ) -> List[int]:
        """
        Sign an TypedData TypedDict for off-chain usage with the starknet private key and return the signature
        This adds a message prefix, so it can't be interchanged with transactions

        :param typed_data:
            TypedData TypedDict to be signed

             .. deprecated:: 0.13.0
                TypedData as dict has been deprecated as possible argument.
                Use :py:class:`starknet_py.utils.TypedData` instead
        :param account_address: account address
        :return: the signature of the JSON object
        """
