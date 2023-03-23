from enum import Enum
from typing import Dict, List, Sequence

# Using cairo-lang methods is a temporary solution until we integrate poseidon hash into the library
from starkware.starknet.core.os.contract_class.class_hash import (
    compute_class_hash as sw_compute_sierra_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    ContractClass as CairoLangContractClass,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    ContractEntryPoint,
    EntryPointType,
)

from starknet_py.common import int_from_bytes
from starknet_py.constants import DEFAULT_ENTRY_POINT_SELECTOR
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.hash.utils import compute_hash_on_elements
from starknet_py.net.client_models import (
    ContractClass,
    SierraContractClass,
    SierraEntryPoint,
    SierraEntryPointsByType,
)


class TransactionHashPrefix(Enum):
    DECLARE = int_from_bytes(b"declare")
    DEPLOY = int_from_bytes(b"deploy")
    DEPLOY_ACCOUNT = int_from_bytes(b"deploy_account")
    INVOKE = int_from_bytes(b"invoke")
    L1_HANDLER = int_from_bytes(b"l1_handler")


# pylint: disable=too-many-arguments
def compute_transaction_hash(
    tx_hash_prefix: TransactionHashPrefix,
    version: int,
    contract_address: int,
    entry_point_selector: int,
    calldata: Sequence[int],
    max_fee: int,
    chain_id: int,
    additional_data: Sequence[int],
) -> int:
    """
    Calculates the transaction hash in the StarkNet network - a unique identifier of the
    transaction.
    The transaction hash is a hash chain of the following information:
        1. A prefix that depends on the transaction type.
        2. The transaction's version.
        3. Contract address.
        4. Entry point selector.
        5. A hash chain of the calldata.
        6. The transaction's maximum fee.
        7. The network's chain ID.
    Each hash chain computation begins with 0 as initialization and ends with its length appended.
    The length is appended in order to avoid collisions of the following kind:
    H([x,y,z]) = h(h(x,y),z) = H([w, z]) where w = h(x,y).

    :param tx_hash_prefix: A prefix that depends on the transaction type.
    :param version: The transaction's version.
    :param contract_address: Contract address.
    :param entry_point_selector: Entry point selector.
    :param calldata: Calldata of the transaction.
    :param max_fee: The transaction's maximum fee.
    :param chain_id: The network's chain ID.
    :param additional_data: Additional data, required for some transactions (e.g. DeployAccount, Declare).
    :return: Hash of the transaction.
    """
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
    """
    Computes hash of the DeployAccount transaction.

    :param version: The transaction's version.
    :param contract_address: Contract address.
    :param class_hash: The class hash of the contract.
    :param constructor_calldata: Constructor calldata of the contract.
    :param max_fee: The transaction's maximum fee.
    :param nonce: Nonce of the transaction.
    :param salt: The contract's address salt.
    :param chain_id: The network's chain ID.
    :return: Hash of the transaction.
    """
    return compute_transaction_hash(
        tx_hash_prefix=TransactionHashPrefix.DEPLOY_ACCOUNT,
        version=version,
        contract_address=contract_address,
        entry_point_selector=DEFAULT_ENTRY_POINT_SELECTOR,
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
    """
    Computes hash of the Declare transaction.

    :param contract_class: ContractClass of the contract.
    :param chain_id: The network's chain ID.
    :param sender_address: Address which sends the transaction.
    :param max_fee: The transaction's maximum fee.
    :param version: The transaction's version.
    :param nonce: Nonce of the transaction.
    :return: Hash of the transaction.
    """
    class_hash = compute_class_hash(contract_class=contract_class)

    return compute_transaction_hash(
        tx_hash_prefix=TransactionHashPrefix.DECLARE,
        version=version,
        contract_address=sender_address,
        entry_point_selector=DEFAULT_ENTRY_POINT_SELECTOR,
        calldata=[class_hash],
        max_fee=max_fee,
        chain_id=chain_id,
        additional_data=[nonce],
    )


def compute_declare_v2_transaction_hash(
    *,
    contract_class: SierraContractClass,
    compiled_class_hash: int,
    chain_id: int,
    sender_address: int,
    max_fee: int,
    version: int,
    nonce: int,
) -> int:
    """
    Computes class hash of declare transaction version 2.

    :param contract_class: SierraContractClass of the contract.
    :param compiled_class_hash: compiled class hash of the program.
    :param chain_id: The network's chain ID.
    :param sender_address: Address which sends the transaction.
    :param max_fee: The transaction's maximum fee.
    :param version: The transaction's version.
    :param nonce: Nonce of the transaction.
    :return: Hash of the transaction.
    """
    class_hash = sw_compute_sierra_class_hash(
        contract_class=_convert_contract_class_to_cairo_lang_format(contract_class)
    )

    return compute_transaction_hash(
        tx_hash_prefix=TransactionHashPrefix.DECLARE,
        version=version,
        contract_address=sender_address,
        entry_point_selector=DEFAULT_ENTRY_POINT_SELECTOR,
        calldata=[class_hash],
        max_fee=max_fee,
        chain_id=chain_id,
        additional_data=[nonce, compiled_class_hash],
    )


def _convert_contract_class_to_cairo_lang_format(
    contract_class: SierraContractClass,
) -> CairoLangContractClass:
    # noinspection PyArgumentList
    return CairoLangContractClass(
        contract_class_version=contract_class.contract_class_version,
        sierra_program=[int(i, 16) for i in contract_class.sierra_program],
        entry_points_by_type=_convert_entry_points(contract_class.entry_points_by_type),
        abi=contract_class.abi,
    )


def _convert_entry_points(
    entry_points: SierraEntryPointsByType,
) -> Dict[EntryPointType, List[ContractEntryPoint]]:
    return {
        EntryPointType.EXTERNAL: _convert_entry_points_for_type(entry_points.external),
        EntryPointType.L1_HANDLER: _convert_entry_points_for_type(
            entry_points.l1_handler
        ),
        EntryPointType.CONSTRUCTOR: _convert_entry_points_for_type(
            entry_points.constructor
        ),
    }


def _convert_entry_points_for_type(
    entry_points: List[SierraEntryPoint],
) -> List[ContractEntryPoint]:
    return [
        ContractEntryPoint(
            selector=entry_point.selector, function_idx=entry_point.function_idx
        )
        for entry_point in entry_points
    ]
