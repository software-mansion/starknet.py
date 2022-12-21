from enum import Enum
from typing import Sequence

from starkware.starknet.core.os.class_hash import compute_class_hash

from starknet_py.common import int_from_bytes
from starknet_py.constants import QUERY_VERSION_BASE
from starknet_py.net.client_models import ContractClass
from starknet_py.utils.crypto.facade import compute_hash_on_elements


class TransactionHashPrefix(Enum):
    DECLARE = int_from_bytes(b"declare")
    DEPLOY = int_from_bytes(b"deploy")
    DEPLOY_ACCOUNT = int_from_bytes(b"deploy_account")
    INVOKE = int_from_bytes(b"invoke")
    L1_HANDLER = int_from_bytes(b"l1_handler")


# pylint: disable=too-many-arguments
def compute_transaction_hash_common(
    tx_hash_prefix: TransactionHashPrefix,
    version: int,
    contract_address: int,
    entry_point_selector: int,
    calldata: Sequence[int],
    max_fee: int,
    chain_id: int,
    additional_data: Sequence[int],
) -> int:
    calldata_hash = compute_hash_on_elements(data=calldata)
    data_to_hash = [
        tx_hash_prefix.value,
        version,
        contract_address,
        entry_point_selector,
        calldata_hash,
        max_fee,
        chain_id,
        *additional_data,
    ]

    return compute_hash_on_elements(
        data=data_to_hash,
    )


def compute_deploy_account_transaction_hash(
    version: int,
    contract_address: int,
    class_hash: int,
    constructor_calldata: Sequence[int],
    max_fee: int,
    nonce: int,
    salt: int,
    chain_id: int,
) -> int:
    return compute_transaction_hash_common(
        tx_hash_prefix=TransactionHashPrefix.DEPLOY_ACCOUNT,
        version=version,
        contract_address=contract_address,
        entry_point_selector=0,
        calldata=[class_hash, salt, *constructor_calldata],
        max_fee=max_fee,
        chain_id=chain_id,
        additional_data=[nonce],
    )


def compute_declare_transaction_hash(
    contract_class: ContractClass,
    chain_id: int,
    sender_address: int,
    max_fee: int,
    version: int,
    nonce: int,
) -> int:
    class_hash = compute_class_hash(contract_class=contract_class)

    if version in [0, QUERY_VERSION_BASE]:
        calldata = []
        additional_data = [class_hash]
    else:
        calldata = [class_hash]
        additional_data = [nonce]

    return compute_transaction_hash_common(
        tx_hash_prefix=TransactionHashPrefix.DECLARE,
        version=version,
        contract_address=sender_address,
        entry_point_selector=0,
        calldata=calldata,
        max_fee=max_fee,
        chain_id=chain_id,
        additional_data=additional_data,
    )
