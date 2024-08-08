from dataclasses import dataclass
from secrets import token_bytes

from eth_keyfile.keyfile import extract_key_from_keyfile

from starknet_py.constants import FIELD_PRIME
from starknet_py.hash.utils import private_to_stark_key
from starknet_py.net.client_models import Hash


@dataclass
class KeyPair:
    private_key: int
    public_key: int

    def __init__(self, private_key: Hash, public_key: Hash):
        if isinstance(private_key, str):
            self.private_key = int(private_key, 0)
        else:
            self.private_key = private_key

        if isinstance(public_key, str):
            self.public_key = int(public_key, 0)
        else:
            self.public_key = public_key

    @staticmethod
    def generate() -> "KeyPair":
        """
        Create a key pair from a randomly generated private key.

        :return: KeyPair object.
        """
        random_int = int.from_bytes(token_bytes(32), byteorder="big")
        private_key = random_int % FIELD_PRIME
        public_key = private_to_stark_key(private_key)
        return KeyPair(private_key=private_key, public_key=public_key)

    @staticmethod
    def from_private_key(key: Hash) -> "KeyPair":
        if isinstance(key, str):
            key = int(key, 0)
        return KeyPair(private_key=key, public_key=private_to_stark_key(key))

    @staticmethod
    def from_keystore(path: str, password: str) -> "KeyPair":
        """
        Create a key pair from a keystore file.
        The keystore file should follow the Ethereum keystore format.

        :param path: Path to the keystore file.
        :param password: Password to decrypt the keystore file.
        :return: KeyPair object.
        """
        key = extract_key_from_keyfile(path, password)
        return KeyPair.from_private_key(int.from_bytes(key, byteorder="big"))
