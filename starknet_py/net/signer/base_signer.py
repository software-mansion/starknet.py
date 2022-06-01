from abc import ABC, abstractmethod
from typing import Tuple

from starknet_py.net.models.transaction import Transaction


class BaseSigner(ABC):
    @abstractmethod
    def public_key(self) -> int:
        """
        Get public key

        :return: public key
        """

    @abstractmethod
    def private_key(self) -> int:
        """
        Get private key

        :return: private key
        """

    @abstractmethod
    def sign_transaction(self, transaction: Transaction) -> Tuple[int, int]:
        """
        Sign a transaction and return signature as two integers 'r' and 's'

        :param transaction: Transaction to sign]
        :return: transaction signature
        """
