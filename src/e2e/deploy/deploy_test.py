import pytest
from starkware.starkware_utils.error_handling import StarkErrorCode

from src.e2e.utils import DevnetClient, file_from_directory

# Mock contract for deployment
import os

directory = os.path.dirname(__file__)


@pytest.mark.asyncio
async def test_deploy_tx():
    client = DevnetClient()
    file_path = file_from_directory(directory, "example-compiled.json")

    contract_def = open(file_path, "r").read()
    result = await client.deploy_contract(contract_def)
    assert result["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name
