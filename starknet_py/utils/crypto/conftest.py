import json
import os
from pathlib import Path
import pytest

# pylint: disable=unused-import
from starknet_py.tests.e2e.conftest import (
    create_gateway_client,
    gateway_account_client,
    address_and_private_key,
    create_account_client,
    run_devnet,
    start_devnet,
    get_available_port,
    pytest_addoption,
)
from starknet_py.utils.typed_data.types import StarkNetDomain, TypedData

directory = Path(os.path.dirname(__file__))


@pytest.fixture(name="typed_data")
def fixture_typed_data() -> dict:
    file_path = directory / "typed_data_example.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    domain = StarkNetDomain(
        name=data["domain"]["name"],
        version=data["domain"]["version"],
        chainId=data["domain"]["chainId"],
    )

    typed_data = TypedData(
        types=data["types"],
        primary_type=data["primaryType"],
        domain=domain,
        message=data["message"],
    )

    return typed_data
