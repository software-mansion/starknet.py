from abc import ABC, abstractmethod
from typing import List

from starknet_py.net.models.transaction import Transaction


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
    def sign_transaction(
        self,
        transaction: Transaction,
    ) -> List[int]:
        """
        Sign execute transaction and return a signature

        :param transaction: Execute transaction to sign
        :return: transaction signature
        """
