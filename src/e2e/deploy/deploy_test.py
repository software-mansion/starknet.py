import pytest
import os
from starkware.starkware_utils.error_handling import StarkErrorCode

from src.e2e.utils import DevnetClient
from src.utils.compiler.starknet_compile import CairoSourceFile
from src.utils.files import file_from_directory

directory = os.path.dirname(__file__)


@pytest.mark.asyncio
async def test_deploy_tx():
    client = DevnetClient()
    map_filename = file_from_directory(directory, "map.cairo")
    map_source_code = open(map_filename).read()

    result = await client.compile_and_deploy_contract(
        [CairoSourceFile(name=map_filename, content=map_source_code)]
    )
    assert result["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name
