from typing import List

from bip_utils import Bip32Path, Bip32Utils, Bip32KeyIndex
from ledgerwallet.client import LedgerClient
from ledgerwallet.transport import enumerate_devices

from starknet_py.net.models import AccountTransaction
from starknet_py.net.signer import BaseSigner
from starknet_py.utils.typed_data import TypedData

STARKNET_CLA = 0x5A
EIP_2645_PURPOSE = 0x80000A55
EIP_2645_PATH_LENGTH = 6
PUBLIC_KEY_SIZE = 65


def _parse_derivation_path_str(derivation_path_str) -> Bip32Path:
    if not derivation_path_str:
        raise ValueError("Empty derivation path")

    path_parts = derivation_path_str.lstrip("m/").split("/")
    path_elements = []
    for part in path_parts:
        if part.endswith("'"):
            index = Bip32Utils.HardenIndex(int(part[:-1]))
        else:
            index = int(part)
        path_elements.append(Bip32KeyIndex(index))

    if len(path_elements) != EIP_2645_PATH_LENGTH:
        raise ValueError(f"Derivation path is not {EIP_2645_PATH_LENGTH}-level long")
    if path_elements[0] != EIP_2645_PURPOSE:
        raise ValueError("Derivation path is not prefixed with m/2645.")

    return Bip32Path(path_elements)


class LedgerStarknetApp:
    def __init__(self, client: LedgerClient):
        self.client = client

    def get_public_key(self, derivation_path: str, display: bool = False):
        pass


class LedgerSigner(BaseSigner):
    def __init__(self, derivation_path_str: str):
        """
        :param derivation_path_str: Derivation path string of the account.
        """
        self.derivation_path = _parse_derivation_path_str(derivation_path_str)

        devices = enumerate_devices()
        if not devices:
            raise Exception("No Ledger devices found")

        self.client = LedgerClient(device=devices[0], cla=STARKNET_CLA)
        self.app = LedgerStarknetApp(self.client)

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


# signer = LedgerSigner("m/2645'/1195502025'/1470455285'/0'/0'/0")
