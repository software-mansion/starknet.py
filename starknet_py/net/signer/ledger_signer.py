from typing import List

from ledgerwallet.client import LedgerClient

from starknet_py.net.models import AccountTransaction
from starknet_py.net.signer import BaseSigner
from starknet_py.utils.typed_data import TypedData

STARKNET_CLA = 0x5A


class LedgerStarknetApp:
    def __init__(self):
        self.client = LedgerClient(cla=STARKNET_CLA)

    def get_public_key(self, derivation_path: str, display: bool):
        pass


class LedgerSigner(BaseSigner):
    def __init__(self, derivation_path: str):
        """
        :param derivation_path: Derivation path of the account.
        """
        self.derivation_path = derivation_path
        self.app = LedgerStarknetApp()

    @property
    def public_key(self) -> int:
        return 0

    @property
    def private_key(self) -> int:
        return 0

    def sign_transaction(self, transaction: AccountTransaction) -> List[int]:
        return [0]

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        return [0]
