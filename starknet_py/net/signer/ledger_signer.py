from typing import List

from bip_utils import Bip32KeyIndex, Bip32Path, Bip32Utils
from ledgerwallet.client import LedgerClient

from starknet_py.constants import EIP_2645_PATH_LENGTH, EIP_2645_PURPOSE, STARKNET_CLA, PUBLIC_KEY_SIZE, SIGNATURE_SIZE
from starknet_py.net.models import AccountTransaction
from starknet_py.net.models.chains import ChainId
from starknet_py.net.signer import BaseSigner
from starknet_py.utils.typed_data import TypedData


def _parse_derivation_path_str(derivation_path_str) -> Bip32Path:
    """
    Parse a derivation path string to a Bip32Path object.

    :param derivation_path_str: Derivation path string.
    """
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


def _derivation_path_to_bytes(derivation_path: Bip32Path) -> bytes:
    """
    Convert a derivation path to a bytes object.

    :param derivation_path: Derivation path.
    """
    return b"".join(index.ToBytes() for index in derivation_path)


class LedgerStarknetApp:
    def __init__(self):
        self.client = LedgerClient(cla=STARKNET_CLA)

    def get_public_key(self, derivation_path: Bip32Path, device_confirmation: bool = False) -> int:
        """
        Get the public key for the given derivation path.

        :param derivation_path: Derivation path of the account.
        :param device_confirmation: Whether to display confirmation on the device for extra security.
        """

        data = _derivation_path_to_bytes(derivation_path)
        response = self.client.apdu_exchange(
            ins=0x01,
            data=data,
            p1=0x01 if device_confirmation else 0x00,
            p2=0x00,
        )

        if len(response) != PUBLIC_KEY_SIZE:
            raise ValueError(
                f"Unexpected response length (expected: {PUBLIC_KEY_SIZE}, actual: {len(data)}"
            )

        public_key = int.from_bytes(response[1:33], byteorder="big")
        return public_key

    def sign_hash(self, derivation_path: Bip32Path, hash_val: int) -> List[int]:
        """
        Request a signature for a raw hash with the given derivation path.
        Currently, the Ledger app only supports blind signing raw hashes.

        :param derivation_path: Derivation path of the account.
        :param hash_val: Hash to sign.
        """

        # sign hash command 1
        data = _derivation_path_to_bytes(derivation_path)
        self.client.apdu_exchange(
            ins=0x02,
            data=data,
            p1=0x00,
            p2=0x00,
        )

        # for some reason ledger the Ledger app expects the data to be left shifted by 4 bits
        shifted_int = hash_val << 4

        shifted_bytes = shifted_int.to_bytes(32, byteorder="big")
        response = self.client.apdu_exchange(
            ins=0x02,
            data=shifted_bytes,
            p1=0x01,
            p2=0x00,
        )

        if len(data) != SIGNATURE_SIZE + 1 or data[0] != SIGNATURE_SIZE:
            raise ValueError(
                f"Unexpected response length (expected: {SIGNATURE_SIZE}, actual: {len(data)}"
            )

        r, s = int.from_bytes(response[1:33], byteorder="big"), int.from_bytes(response[33:65], byteorder="big")
        return [r, s]


class LedgerSigner(BaseSigner):
    def __init__(self, derivation_path_str: str, chain_id: ChainId):
        """
        :param derivation_path_str: Derivation path string of the account.
        :param chain_id: ChainId of the chain.
        """

        self.app = LedgerStarknetApp()
        self.derivation_path = _parse_derivation_path_str(derivation_path_str)
        self.chain_id = chain_id

    @property
    def public_key(self) -> int:
        return self.app.get_public_key(derivation_path=self.derivation_path)

    def sign_transaction(self, transaction: AccountTransaction) -> List[int]:
        tx_hash = transaction.calculate_hash(self.chain_id)
        return self.app.sign_hash(derivation_path=self.derivation_path, hash_val=tx_hash)

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        msg_hash = typed_data.message_hash(account_address)
        return self.app.sign_hash(derivation_path=self.derivation_path, hash_val=msg_hash)
