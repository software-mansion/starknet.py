import os

import pytest

from starknet.contract import Contract
from starknet.tests.e2e.utils import DevnetClient

directory = os.path.dirname(__file__)
map_filename = os.path.join(directory, "map.cairo")
map_source_code = open(map_filename).read()


@pytest.mark.asyncio
@pytest.mark.parametrize("key, value", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_and_call(key, value):
    client = DevnetClient()

    # Deploy simple k-v store
    contract = await Contract.deploy(client=client, compilation_source=map_source_code)
    await contract.functions.put.invoke(key, value)
    (response,) = await contract.functions.get.call(key)

    assert response == value
