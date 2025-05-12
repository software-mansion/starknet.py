import hashlib
from enum import Enum
from typing import TYPE_CHECKING, List

from starknet_py.hash.address import compute_address
from starknet_py.hash.transaction import TransactionHashPrefix
from starknet_py.net.client_models import Call
from starknet_py.net.models import DeclareV3, DeployAccountV3, AccountTransaction
from starknet_py.net.models.chains import ChainId
from starknet_py.net.models.transaction import InvokeV3, _AccountTransactionV3
from starknet_py.net.signer import BaseSigner
from starknet_py.utils.typed_data import TypedData

STARKNET_CLA = 0x5A
EIP_2645_PURPOSE = 0x80000A55
PUBLIC_KEY_RESPONSE_LENGTH = 65
SIGNATURE_RESPONSE_LENGTH = 65
VERSION_RESPONSE_LENGTH = 3


class LateException:
    def __init__(self, exc: Exception):
        self.exc = exc

    def __getattr__(self, item):
        raise self.exc

    def __call__(self, *args, **kwargs):
        self.__getattr__("exc")


try:
    from ledgerwallet.client import LedgerClient
except ImportError as e:
    if TYPE_CHECKING:
        raise
    dummy = LateException(e)
    LedgerClient = dummy


class LedgerStarknetApp:
    def __init__(self, account_id: int = 0, application_name: str = "LedgerW"):
        """
        :param account_id: ID of Ledger account.
        :param application_name: Name of the application, which is part of ERC2645 derivation path.
        """
        self.client: LedgerClient = LedgerClient(cla=STARKNET_CLA)
        self.derivation_path = _get_derivation_path(
            account_id=account_id, application_name=application_name
        )

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

    def get_public_key(self, device_confirmation: bool = False) -> int:
        """
        Get public key for the given derivation path.

        :param device_confirmation: Whether to display confirmation on the device for extra security.
        :return: Public key.
        """

        response = self.client.apdu_exchange(
            ins=1,
            data=self.derivation_path,
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

    def set_private_key(self, ins: int):
        """
        Set the private key.

        :param ins: Instruction ID.
        """
        self.client.apdu_exchange(ins=ins, data=self.derivation_path)


class LedgerSigningMode(Enum):
    """
    Enum representing signing modes for Ledger
    """

    CLEAR = "clear"
    BLIND = "blind"


class LedgerSigner(BaseSigner):
    def __init__(
        self,
        chain_id: ChainId,
        account_id: int = 0,
        application_name: str = "LedgerW",
        signing_mode: LedgerSigningMode = LedgerSigningMode.CLEAR,
    ):
        """
        :param chain_id: Chain ID.
        :param account_id: ID of Ledger account.
        :param application_name: Name of the application, which is part of ERC2645 derivation path.
        :param signing_mode: Signing mode (clear or blind).
        """
        self.app: LedgerStarknetApp = LedgerStarknetApp()
        self.account_id: int = account_id
        self.application_name: str = application_name
        self.chain_id: ChainId = chain_id
        self.signing_mode: LedgerSigningMode = signing_mode

    @property
    def public_key(self) -> int:
        return self.app.get_public_key()

    def sign_transaction(self, transaction: AccountTransaction) -> List[int]:
        if self.signing_mode == LedgerSigningMode.CLEAR:
            if isinstance(transaction, DeclareV3):
                raise ValueError("DeclareV3 signing is not supported bye LedgerSigner")
            if isinstance(transaction, DeployAccountV3):
                return self._sign_deploy_account_v3(transaction)
            if isinstance(transaction, InvokeV3):
                return self._sign_invoke_transaction_v3(transaction)
            raise ValueError(f"Unsupported transaction type: {type(transaction)}")

        tx_hash = transaction.calculate_hash(self.chain_id)
        return self.app.sign_hash(hash_val=tx_hash)

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        msg_hash = typed_data.message_hash(account_address)
        return self.app.sign_hash(hash_val=msg_hash)

    # pylint: disable=no-self-use
    def _decode_signature(self, response: bytes) -> List[int]:
        r = int.from_bytes(response[33:65], byteorder="big")
        s = int.from_bytes(response[65:97], byteorder="big")
        return [r, s]

    def _sign_deploy_account_v3(self, tx: DeployAccountV3) -> List[int]:
        # pylint: disable=too-many-locals
        # Command 0: set private key
        self.app.set_private_key(ins=5)

        # Command 1: Send deploy account tx fields
        contract_address = compute_address(
            salt=tx.contract_address_salt,
            class_hash=tx.class_hash,
            constructor_calldata=tx.constructor_calldata,
            deployer_address=0,
        )
        account_address_bytes = contract_address.to_bytes(32, byteorder="big")
        chain_id_bytes = self.chain_id.to_bytes(32, byteorder="big")
        nonce_bytes = tx.nonce.to_bytes(32, byteorder="big")
        common_tx_fields = tx.get_common_fields(
            tx_prefix=TransactionHashPrefix.DEPLOY,
            address=contract_address,
            chain_id=self.chain_id,
        )
        da_mode_hash_bytes = common_tx_fields.get_data_availability_modes().to_bytes(
            32, byteorder="big"
        )
        class_hash_bytes = tx.class_hash.to_bytes(32, byteorder="big")
        salt_bytes = tx.contract_address_salt.to_bytes(32, byteorder="big")
        data = (
            account_address_bytes
            + chain_id_bytes
            + nonce_bytes
            + da_mode_hash_bytes
            + class_hash_bytes
            + salt_bytes
        )

        self.app.client.apdu_exchange(
            ins=5,
            data=data,
            p1=1,
            p2=0,
        )

        # Command 2: fees
        fee_bytes = self._encode_fee(
            tx=tx,
            tx_prefix=TransactionHashPrefix.DEPLOY_ACCOUNT,
            address=contract_address,
        )
        self.app.client.apdu_exchange(
            ins=5,
            data=fee_bytes,
            p1=2,
            p2=0,
        )

        # Command 3: Send paymaster data
        paymaster_bytes = b"".join(
            val.to_bytes(32, byteorder="big") for val in tx.paymaster_data
        )
        self.app.client.apdu_exchange(
            ins=5,
            data=paymaster_bytes,
            p1=3,
            p2=0,
        )

        # Command 4: Number of constructor calldata
        constructor_length_bytes = len(tx.constructor_calldata).to_bytes(
            32, byteorder="big"
        )
        self.app.client.apdu_exchange(
            ins=5,
            data=constructor_length_bytes,
            p1=4,
            p2=0,
        )

        # Command 5: Send constructor calldata
        constructor_bytes = b"".join(
            val.to_bytes(32, byteorder="big") for val in tx.constructor_calldata
        )
        constructor_chunks = []
        chunk_size = 7 * 32  # 224 bytes
        for i in range(0, len(constructor_bytes), chunk_size):
            constructor_chunks.append(constructor_bytes[i : i + chunk_size])

        response = None

        for chunk in constructor_chunks:
            response = self.app.client.apdu_exchange(
                ins=5,
                data=chunk,
                p1=5,
                p2=0,
            )

        if response is None:
            raise ValueError("No response received from Ledger device.")

        return self._decode_signature(response)

    def _sign_invoke_transaction_v3(self, tx: InvokeV3) -> List[int]:
        # pylint: disable=too-many-locals
        # Command 0: set private key
        self.app.set_private_key(ins=3)

        # Command 1: Send invoke tx fields
        sender_address_bytes = tx.sender_address.to_bytes(32, byteorder="big")
        chain_id_bytes = self.chain_id.to_bytes(32, byteorder="big")
        nonce_bytes = tx.nonce.to_bytes(32, byteorder="big")
        common_tx_fields = tx.get_common_fields(
            tx_prefix=TransactionHashPrefix.INVOKE,
            address=tx.sender_address,
            chain_id=self.chain_id,
        )
        da_mode_hash_bytes = common_tx_fields.get_data_availability_modes().to_bytes(
            32, byteorder="big"
        )
        data = sender_address_bytes + chain_id_bytes + nonce_bytes + da_mode_hash_bytes
        self.app.client.apdu_exchange(
            ins=3,
            data=data,
            p1=1,
            p2=0,
        )

        # Command 2: Fees
        fee_bytes = self._encode_fee(
            tx=tx,
            tx_prefix=TransactionHashPrefix.INVOKE,
            address=tx.sender_address,
        )
        self.app.client.apdu_exchange(
            ins=3,
            data=fee_bytes,
            p1=2,
            p2=0,
        )

        # Command 3: Send paymaster data
        paymaster_bytes = b"".join(
            val.to_bytes(32, byteorder="big") for val in tx.paymaster_data
        )
        self.app.client.apdu_exchange(
            ins=3,
            data=paymaster_bytes,
            p1=3,
            p2=0,
        )

        # Command 4: Send account deployment data
        account_deployment_bytes = b"".join(
            val.to_bytes(32, byteorder="big") for val in tx.account_deployment_data
        )
        self.app.client.apdu_exchange(
            ins=3,
            data=account_deployment_bytes,
            p1=4,
            p2=0,
        )

        # Command 5: Number of calls
        # InvokeV3 stores serialized calls in calldata
        # index 0 is the number of calls (because of Starknet's array serialization)
        num_calls = tx.calldata[0]
        num_calls_bytes = num_calls.to_bytes(32, byteorder="big")
        self.app.client.apdu_exchange(
            ins=3,
            data=num_calls_bytes,
            p1=5,
            p2=0,
        )

        # Command 6: Send calls
        response = None
        calls = _deserialize_invoke_tx_calldata_to_calls(tx.calldata)

        for call in calls:
            calldatas = _encode_call(call)

            response = self.app.client.apdu_exchange(
                ins=3,
                data=bytes(calldatas[0]),
                p1=6,
                p2=0,
            )

            if len(calldatas) == 1:
                continue

            for part in calldatas[1:]:
                response = self.app.client.apdu_exchange(ins=3, p1=6, p2=1, data=part)

        if response is None:
            raise ValueError("No response received from Ledger device.")

        return self._decode_signature(response)

    def _encode_fee(
        self,
        tx: _AccountTransactionV3,
        tx_prefix: TransactionHashPrefix,
        address: int,
    ) -> bytes:
        tip_bytes = tx.tip.to_bytes(32, byteorder="big")
        common_tx_fields = tx.get_common_fields(
            tx_prefix=tx_prefix,
            address=address,
            chain_id=self.chain_id,
        )
        l1_gas_bounds, l2_gas_bounds, l1_data_gas_bounds = (
            common_tx_fields.compute_resource_bounds_for_fee()
        )
        l1_gas_bytes = l1_gas_bounds.to_bytes(32, byteorder="big")
        l2_gas_bytes = l2_gas_bounds.to_bytes(32, byteorder="big")
        l1_data_gas_bytes = l1_data_gas_bounds.to_bytes(32, byteorder="big")
        return tip_bytes + l1_gas_bytes + l2_gas_bytes + l1_data_gas_bytes


def _deserialize_invoke_tx_calldata_to_calls(tx_calldata: List[int]) -> List[Call]:
    num_calls = tx_calldata[0]
    offset = 1
    calls = []

    for _ in range(num_calls):
        address = tx_calldata[offset]
        offset += 1
        selector = tx_calldata[offset]
        offset += 1
        call_calldata_length = tx_calldata[offset]
        offset += 1
        call_calldata = []

        if call_calldata_length > 0:
            for _ in range(call_calldata_length):
                call_calldata.append(tx_calldata[offset])
                offset += 1

        call = Call(
            to_addr=address,
            selector=selector,
            calldata=call_calldata,
        )
        calls.append(call)

    return calls


def _string_to_4byte_hash(s: str):
    num = int.from_bytes(hashlib.sha256(s.encode()).digest(), "big")
    masked = num & 0x7FFFFFFF
    return masked.to_bytes(4, "big")


def _encode_call(call: Call) -> List[bytes]:
    to_addr_bytes = call.to_addr.to_bytes(32, byteorder="big")
    selector_bytes = call.selector.to_bytes(32, byteorder="big")

    if call.calldata:
        calldata_size_bytes = len(call.calldata).to_bytes(32, byteorder="big")
        calldata_bytes = calldata_size_bytes + b"".join(
            val.to_bytes(32, byteorder="big") for val in call.calldata
        )
    else:
        calldata_bytes = int(0).to_bytes(32, byteorder="big")
    call_bytes = to_addr_bytes + selector_bytes + calldata_bytes
    calldatas = []

    chunk_size = 7 * 32  # 224 bytes
    for i in range(0, len(call_bytes), chunk_size):
        calldatas.append(call_bytes[i : i + chunk_size])

    return calldatas


def _get_derivation_path(
    account_id: int,
    application_name: str,
) -> bytes:
    purpose_bytes = EIP_2645_PURPOSE.to_bytes(4, byteorder="big")  # EIP2645
    coin_type_bytes = b"GA\xe9\xc9"  # "starknet"

    if application_name == "LedgerW":
        application_bytes = (
            (43).to_bytes(1, byteorder="big")
            + (206).to_bytes(1, byteorder="big")
            + (231).to_bytes(1, byteorder="big")
            + (219).to_bytes(1, byteorder="big")
        )
    else:
        application_bytes = _string_to_4byte_hash(application_name)

    hardened_zero_bytes = (0).to_bytes(4, byteorder="big")
    account_bytes = account_id.to_bytes(4, byteorder="big")
    address_index_bytes = (0).to_bytes(4, byteorder="big")

    return (
        purpose_bytes
        + coin_type_bytes
        + application_bytes
        + hardened_zero_bytes
        + account_bytes
        + address_index_bytes
    )
