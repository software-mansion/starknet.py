import os
from pathlib import Path

import pytest

from starknet_py.contract import Contract
from starknet_py.net.client import BadRequest
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

    class_hash = await client.get_class_hash_at(contract_address=contract.address)

    assert class_hash is not None


@pytest.mark.asyncio
async def test_get_class_hash_at_error_when_contract_not_deployed(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(BadRequest) as breq:
        await client.get_class_hash_at(contract_address="0x1")

    assert "Contract with address 0x1 is not deployed" in str(breq.value)


@pytest.mark.asyncio
async def test_get_class_by_hash(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    declare_result = await client.declare(compilation_source=map_source)
    class_hash = declare_result["class_hash"]

    assert await client.get_class_by_hash(class_hash) is not None


@pytest.mark.asyncio
async def test_get_class_by_hash_error_when_contract_not_deployed(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(BadRequest) as breq:
        await client.get_class_by_hash("0x1")

    assert "Class with hash 0x1 is not declared" in str(breq.value)
