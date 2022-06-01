from abc import ABC, abstractmethod
from typing import Tuple

from starknet_py.net.models.transaction import Transaction


class BaseSigner(ABC):
    """
    Base class for transaction signer. Implement methods from this ABC to use a custom signer in AccountClient
    """

    @abstractmethod
    def sign_transaction(self, transaction: Transaction) -> Tuple[int, int]:
        """
        Sign a transaction and return signature as two integers 'r' and 's'

        :param transaction: Transaction to sign]
        :return: transaction signature
        """
