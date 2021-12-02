import pytest
import os

from src.contract import Contract, ContractFunction
from src.e2e.utils import DevnetClient

directory = os.path.dirname(__file__)
map_filename = os.path.join(directory, "map.cairo")
map_source_code = open(map_filename).read()


@pytest.mark.asyncio
async def test_deploy_tx():
    client = DevnetClient()
    result = await Contract.deploy(client=client, compilation_source=map_source_code)
    assert isinstance(result.functions.get, ContractFunction)
    assert isinstance(result.functions.put, ContractFunction)
