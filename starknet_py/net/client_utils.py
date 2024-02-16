import re
from typing import Dict, Union, cast

from typing_extensions import get_args

from starknet_py.hash.utils import encode_uint, encode_uint_list
from starknet_py.net.client_models import (
    Hash,
    L1HandlerTransaction,
    Tag,
    TransactionType,
)
from starknet_py.net.models.transaction import (
    AccountTransaction,
    Declare,
    DeclareV1Schema,
    DeclareV2,
    DeclareV2Schema,
    DeclareV3,
    DeployAccount,
    DeployAccountV3,
    Invoke,
    InvokeV3,
)
from starknet_py.net.schemas.broadcasted import TransactionTraceSchema
from starknet_py.net.schemas.gateway import SierraCompiledContractSchema
from starknet_py.net.schemas.rpc import TransactionV3Schema
from starknet_py.net.schemas.utils import _extract_tx_version


def hash_to_felt(value: Hash) -> str:
    """
    Convert hash to hexadecimal string
    """
    if isinstance(value, str):
        return value

    return hex(value)


def is_block_identifier(value: Union[int, Hash, Tag]) -> bool:
    return isinstance(value, str) and value in get_args(Tag)


def encode_l1_message(tx: L1HandlerTransaction) -> bytes:
    from_address = tx.calldata[0]
    # Pop first element to have in calldata the actual payload
    tx.calldata.pop(0)

    return (
        encode_uint(from_address)
        + encode_uint(tx.contract_address)
        + encode_uint(tx.nonce)
        + encode_uint(tx.entry_point_selector)
        + encode_uint(len(tx.calldata))
        + encode_uint_list(tx.calldata)
    )


def _to_storage_key(key: int) -> str:
    """
    Convert a value to RPC storage key matching a ``^0x0[0-7]{1}[a-fA-F0-9]{0,62}$`` pattern.

    :param key: The key to convert.
    :return: RPC storage key representation of the key.
    """

    hashed_key = hex(key)[2:]

    if hashed_key[0] not in ("0", "1", "2", "3", "4", "5", "6", "7"):
        hashed_key = "0" + hashed_key

    hashed_key = "0x0" + hashed_key

    if not re.match(r"^0x0[0-7]{1}[a-fA-F0-9]{0,62}$", hashed_key):
        raise ValueError(f"Value {key} cannot be represented as RPC storage key.")

    return hashed_key


def _to_rpc_felt(value: Hash) -> str:
    """
    Convert the value to RPC felt matching a ``^0x(0|[a-fA-F1-9]{1}[a-fA-F0-9]{0,62})$`` pattern.

    :param value: The value to convert.
    :return: RPC felt representation of the value.
    """
    if isinstance(value, str):
        value = int(value, 16)

    rpc_felt = hex(value)
    assert re.match(r"^0x(0|[a-fA-F1-9]{1}[a-fA-F0-9]{0,62})$", rpc_felt)
    return rpc_felt


def _is_valid_eth_address(address: str) -> bool:
    """
    A function checking if an address matches Ethereum address regex. Note that it doesn't validate any checksums etc.
    """
    return bool(re.fullmatch("^0x[a-fA-F0-9]{40}$", address))


def _create_broadcasted_txn(transaction: AccountTransaction) -> dict:
    return cast(
        Dict,
        TransactionTraceSchema().dump(obj=transaction),
    )


def _create_broadcasted_txn_prev(transaction: AccountTransaction) -> dict:
    txn_map = {
        TransactionType.DECLARE: _create_broadcasted_declare_properties,
        TransactionType.INVOKE: _create_broadcasted_invoke_properties,
        TransactionType.DEPLOY_ACCOUNT: _create_broadcasted_deploy_account_properties,
    }

    common_properties = _create_broadcasted_txn_common_properties(transaction)
    transaction_specific_properties = txn_map[transaction.type](transaction)

    return {
        **common_properties,
        **transaction_specific_properties,
    }


def _create_broadcasted_declare_properties(
    transaction: Union[Declare, DeclareV2, DeclareV3]
) -> dict:
    if isinstance(transaction, DeclareV2):
        return _create_broadcasted_declare_v2_properties(transaction)
    if isinstance(transaction, DeclareV3):
        return _create_broadcasted_declare_v3_properties(transaction)

    contract_class = cast(Dict, DeclareV1Schema().dump(obj=transaction))[
        "contract_class"
    ]
    declare_properties = {
        "contract_class": {
            "entry_points_by_type": contract_class["entry_points_by_type"],
            "program": contract_class["program"],
        },
        "sender_address": _to_rpc_felt(transaction.sender_address),
    }
    if contract_class["abi"] is not None:
        declare_properties["contract_class"]["abi"] = contract_class["abi"]

    return declare_properties


def _create_broadcasted_declare_v2_properties(transaction: DeclareV2) -> dict:
    contract_class = cast(Dict, DeclareV2Schema().dump(obj=transaction))[
        "contract_class"
    ]
    declare_v2_properties = {
        "contract_class": {
            "entry_points_by_type": contract_class["entry_points_by_type"],
            "sierra_program": contract_class["sierra_program"],
            "contract_class_version": contract_class["contract_class_version"],
        },
        "sender_address": _to_rpc_felt(transaction.sender_address),
        "compiled_class_hash": _to_rpc_felt(transaction.compiled_class_hash),
    }
    if contract_class["abi"] is not None:
        declare_v2_properties["contract_class"]["abi"] = contract_class["abi"]

    return declare_v2_properties


def _create_broadcasted_declare_v3_properties(transaction: DeclareV3) -> dict:
    contract_class = cast(
        Dict, SierraCompiledContractSchema().dump(obj=transaction.contract_class)
    )

    declare_v3_properties = {
        "contract_class": {
            "entry_points_by_type": contract_class["entry_points_by_type"],
            "sierra_program": contract_class["sierra_program"],
            "contract_class_version": contract_class["contract_class_version"],
        },
        "sender_address": _to_rpc_felt(transaction.sender_address),
        "compiled_class_hash": _to_rpc_felt(transaction.compiled_class_hash),
        "account_deployment_data": [
            _to_rpc_felt(data) for data in transaction.account_deployment_data
        ],
    }

    if contract_class["abi"] is not None:
        declare_v3_properties["contract_class"]["abi"] = contract_class["abi"]

    return {
        **_create_broadcasted_txn_v3_common_properties(transaction),
        **declare_v3_properties,
    }


def _create_broadcasted_invoke_properties(transaction: Union[Invoke, InvokeV3]) -> dict:
    invoke_properties = {
        "sender_address": _to_rpc_felt(transaction.sender_address),
        "calldata": [_to_rpc_felt(data) for data in transaction.calldata],
    }

    if isinstance(transaction, InvokeV3):
        return {
            **_create_broadcasted_txn_v3_common_properties(transaction),
            **invoke_properties,
            "account_deployment_data": [
                _to_rpc_felt(data) for data in transaction.account_deployment_data
            ],
        }

    return invoke_properties


def _create_broadcasted_deploy_account_properties(
    transaction: Union[DeployAccount, DeployAccountV3]
) -> dict:
    deploy_account_txn_properties = {
        "contract_address_salt": _to_rpc_felt(transaction.contract_address_salt),
        "constructor_calldata": [
            _to_rpc_felt(data) for data in transaction.constructor_calldata
        ],
        "class_hash": _to_rpc_felt(transaction.class_hash),
    }

    if isinstance(transaction, DeployAccountV3):
        return {
            **_create_broadcasted_txn_v3_common_properties(transaction),
            **deploy_account_txn_properties,
        }

    return deploy_account_txn_properties


def _create_broadcasted_txn_common_properties(transaction: AccountTransaction) -> dict:
    broadcasted_txn_common_properties = {
        "type": transaction.type.name,
        "version": _to_rpc_felt(transaction.version),
        "signature": [_to_rpc_felt(sig) for sig in transaction.signature],
        "nonce": _to_rpc_felt(transaction.nonce),
    }

    if _extract_tx_version(transaction.version) < 3 and hasattr(transaction, "max_fee"):
        broadcasted_txn_common_properties["max_fee"] = _to_rpc_felt(
            transaction.max_fee  # pyright: ignore
        )

    return broadcasted_txn_common_properties


def _create_broadcasted_txn_v3_common_properties(
    transaction: Union[DeclareV3, InvokeV3, DeployAccountV3]
) -> dict:
    return cast(
        Dict,
        TransactionV3Schema(exclude=["version", "signature"]).dump(obj=transaction),
    )
