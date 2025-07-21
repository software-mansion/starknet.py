# pylint: disable=redefined-outer-name

import json
import random
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import pytest

from starknet_py.net.client_models import (
    BlockStatus,
    DAMode,
    InvokeTransactionV3,
    L1DAMode,
    ResourceBounds,
    ResourceBoundsMapping,
    ResourcePrice,
    StarknetBlock,
)
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.typed_data import TypedDataDict
from starknet_py.tests.e2e.fixtures.constants import (
    CONTRACTS_V1_ARTIFACTS_MAP,
    CONTRACTS_V1_COMPILED,
    CONTRACTS_V2_ARTIFACTS_MAP,
    CONTRACTS_V2_COMPILED,
    TYPED_DATA_DIR,
)


def pytest_addoption(parser):
    parser.addoption(
        "--contract_dir",
        action="store",
        default="",
        help="Contract directory: possible 'v1', 'v2'",
    )


@pytest.fixture(
    params=[
        "typed_data_rev_0_example.json",
        "typed_data_rev_0_felt_array_example.json",
        "typed_data_rev_0_long_string_example.json",
        "typed_data_rev_0_struct_array_example.json",
        "typed_data_rev_1_example.json",
    ],
)
def typed_data(request) -> TypedDataDict:
    """
    Returns TypedData dictionary example.
    """
    file_name = getattr(request, "param")
    file_path = TYPED_DATA_DIR / file_name

    with open(file_path, "r", encoding="utf-8") as file:
        typed_data = json.load(file)

    return typed_data


@pytest.fixture(name="get_tx_receipt_path", scope="package")
def get_tx_receipt_full_node_client():
    return f"{FullNodeClient.__module__}.FullNodeClient.get_transaction_receipt"


@pytest.fixture(name="get_tx_status_path", scope="package")
def get_tx_status_full_node_client():
    return f"{FullNodeClient.__module__}.FullNodeClient.get_transaction_status"


@pytest.fixture(name="get_block_with_txs_path", scope="package")
def get_block_with_txs_full_node_client():
    return f"{FullNodeClient.__module__}.FullNodeClient.get_block_with_txs"


def transaction_mock_with_tip(tip: int) -> InvokeTransactionV3:
    return InvokeTransactionV3(
        hash=random.randint(0, 1000),
        signature=[],
        version=3,
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=1, max_price_per_unit=1),
            l2_gas=ResourceBounds(max_amount=1, max_price_per_unit=1),
            l1_data_gas=ResourceBounds(max_amount=1, max_price_per_unit=1),
        ),
        paymaster_data=[],
        nonce_data_availability_mode=DAMode.L2,
        fee_data_availability_mode=DAMode.L2,
        calldata=[],
        sender_address=random.randint(0, 100000),
        nonce=1,
        account_deployment_data=[],
        tip=tip,
    )


def starknet_block_mock() -> StarknetBlock:
    return StarknetBlock(
        block_number=1,
        block_hash=0x123,
        parent_hash=0x111,
        new_root=0x222,
        timestamp=1640000000,
        sequencer_address=0x1,
        l1_gas_price=ResourcePrice(price_in_fri=1, price_in_wei=1),
        l2_gas_price=ResourcePrice(price_in_fri=1, price_in_wei=1),
        l1_data_gas_price=ResourcePrice(price_in_fri=1, price_in_wei=1),
        l1_da_mode=L1DAMode.BLOB,
        starknet_version="0.14.0",
        status=BlockStatus.ACCEPTED_ON_L2,
        transactions=[],
    )


@pytest.fixture(name="block_with_tips_mock", scope="package")
def block_with_tips_mock():
    block = starknet_block_mock()
    block.transactions = [
        transaction_mock_with_tip(2),
        transaction_mock_with_tip(1),
        transaction_mock_with_tip(3),
    ]
    return block


class ContractVersion(Enum):
    V1 = "V1"
    V2 = "V2"


class UnknownArtifacts(BaseException):
    pass


def load_contract(contract_name: str, version: Optional[ContractVersion] = None):
    if version is None:
        if "--contract_dir=v1" in sys.argv:
            version = ContractVersion.V1
        if "--contract_dir=v2" in sys.argv:
            version = ContractVersion.V2

    if version == ContractVersion.V1:
        artifacts_map_path = CONTRACTS_V1_ARTIFACTS_MAP
        directory = CONTRACTS_V1_COMPILED
    else:
        artifacts_map_path = CONTRACTS_V2_ARTIFACTS_MAP
        directory = CONTRACTS_V2_COMPILED

    artifacts_map = json.loads((artifacts_map_path).read_text("utf-8"))

    artifact_file_names = next(
        (
            item["artifacts"]
            for item in artifacts_map["contracts"]
            if item["contract_name"] == contract_name
        ),
        None,
    )

    if not isinstance(artifact_file_names, dict):  # pyright: ignore
        raise UnknownArtifacts(f"Artifacts for contract {contract_name} not found")

    sierra = (directory / artifact_file_names["sierra"]).read_text("utf-8")
    casm = (directory / artifact_file_names["casm"]).read_text("utf-8")

    return {"casm": casm, "sierra": sierra}


def read_contract(file_name: str, *, directory: Path) -> str:
    """
    Return contents of file_name from directory.
    """
    return (directory / file_name).read_text("utf-8")
