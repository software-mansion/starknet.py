from typing import TYPE_CHECKING, List

from starknet_py.constants import (
    EIP_2645_PATH_LENGTH,
    EIP_2645_PURPOSE,
    PUBLIC_KEY_RESPONSE_LENGTH,
    SIGNATURE_RESPONSE_LENGTH,
    STARKNET_CLA,
    VERSION_RESPONSE_LENGTH,
)
from starknet_py.net.models import AccountTransaction
from starknet_py.net.models.chains import ChainId
from starknet_py.net.signer import BaseSigner
from starknet_py.utils.typed_data import TypedData


class LateException:
    def __init__(self, exc: Exception):
        self.exc = exc

    def __getattr__(self, item):
        raise self.exc

    def __call__(self, *args, **kwargs):
        self.__getattr__("exc")


try:
    from bip_utils import Bip32KeyIndex, Bip32Path, Bip32Utils
    from ledgerwallet.client import LedgerClient
except ImportError as e:
    if TYPE_CHECKING:
        raise
    dummy = LateException(e)
    Bip32KeyIndex, Bip32Path, Bip32Utils, LedgerClient = dummy, dummy, dummy, dummy


class LedgerStarknetApp:
    def __init__(self):
        self.client: LedgerClient = LedgerClient(cla=STARKNET_CLA)

    @property
    def version(self) -> str:
        """
        Get the Ledger app version.

        :return: Version string.
        """
        response = self.client.apdu_exchange(ins=0)
        if len(response) != VERSION_RESPONSE_LENGTH:
            raise ValueError(
                f"Unexpected response length (expected: {VERSION_RESPONSE_LENGTH}, actual: {len(response)}"
            )
        major, minor, patch = list(response)
        return f"{major}.{minor}.{patch}"

    def get_public_key(
        self, derivation_path: Bip32Path, device_confirmation: bool = False
    ) -> int:
        """
        Get public key for the given derivation path.

        :param derivation_path: Derivation path of the account.
        :param device_confirmation: Whether to display confirmation on the device for extra security.
        :return: Public key.
        """

        data = _derivation_path_to_bytes(derivation_path)
        response = self.client.apdu_exchange(
            ins=1,
            data=data,
            p1=int(device_confirmation),
            p2=0,
        )

        if len(response) != PUBLIC_KEY_RESPONSE_LENGTH:
            raise ValueError(
                f"Unexpected response length (expected: {PUBLIC_KEY_RESPONSE_LENGTH}, actual: {len(response)}"
            )

        public_key = int.from_bytes(response[1:33], byteorder="big")
        return public_key

    def sign_hash(self, hash_val: int) -> List[int]:
        """
        Request a signature for a raw hash with the given derivation path.
        Currently, the Ledger app only supports blind signing raw hashes.

        :param hash_val: Hash to sign.
        :return: Signature as a list of two integers.
        """

        # for some reason the Ledger app expects the data to be left shifted by 4 bits
        shifted_int = hash_val << 4
        shifted_bytes = shifted_int.to_bytes(32, byteorder="big")

        response = self.client.apdu_exchange(
            ins=0x02,
            data=shifted_bytes,
            p1=0x01,
            p2=0x00,
        )

        if (
            len(response) != SIGNATURE_RESPONSE_LENGTH + 1
            or response[0] != SIGNATURE_RESPONSE_LENGTH
        ):
            raise ValueError(
                f"Unexpected response length (expected: {SIGNATURE_RESPONSE_LENGTH}, actual: {len(response)}"
            )

        r, s = int.from_bytes(response[1:33], byteorder="big"), int.from_bytes(
            response[33:65], byteorder="big"
        )
        return [r, s]


class LedgerSigner(BaseSigner):
    def __init__(self, derivation_path_str: str, chain_id: ChainId):
        """
        :param derivation_path_str: Derivation path string of the account.
        :param chain_id: ChainId of the chain.
        """

        self.app: LedgerStarknetApp = LedgerStarknetApp()
        self.derivation_path: Bip32Path = _parse_derivation_path_str(
            derivation_path_str
        )
        self.chain_id: ChainId = chain_id

    @property
    def public_key(self) -> int:
        return self.app.get_public_key(derivation_path=self.derivation_path)

    def sign_transaction(self, transaction: AccountTransaction) -> List[int]:
        tx_hash = transaction.calculate_hash(self.chain_id)
        return self.app.sign_hash(hash_val=tx_hash)

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        msg_hash = typed_data.message_hash(account_address)
        return self.app.sign_hash(hash_val=msg_hash)


def _parse_derivation_path_str(derivation_path_str: str) -> Bip32Path:
    """
    Parse a derivation path string to a Bip32Path object.

    :param derivation_path_str: Derivation path string.
    :return: Bip32Path object.
    """
    if not derivation_path_str:
        raise ValueError("Empty derivation path")

    path_parts = derivation_path_str.lstrip("m/").split("/")
    path_elements = [
        Bip32KeyIndex(
            Bip32Utils.HardenIndex(int(part[:-1])) if part.endswith("'") else int(part)
        )
        for part in path_parts
    ]

    if len(path_elements) != EIP_2645_PATH_LENGTH:
        raise ValueError(f"Derivation path is not {EIP_2645_PATH_LENGTH}-level long")
    if path_elements[0] != EIP_2645_PURPOSE:
        raise ValueError("Derivation path is not prefixed with m/2645.")

    return Bip32Path(path_elements)


def _derivation_path_to_bytes(derivation_path: Bip32Path) -> bytes:
    """
    Convert a derivation path to a bytes object.

    :param derivation_path: Derivation path.
    :return: Bytes object.
    """
    return b"".join(index.ToBytes() for index in derivation_path)
