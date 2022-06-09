import os
from pathlib import Path

import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)

map_source = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_get_class_hash_at(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    deployment_result = await Contract.deploy(
        compilation_source=map_source, client=client
    )
    await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    await client.get_class_hash_at(contract_address=contract.address)
