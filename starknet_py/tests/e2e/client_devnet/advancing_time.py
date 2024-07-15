import pytest


@pytest.mark.asyncio
async def test_time_advancing(devnet_client):
    time = 3384617820

    await devnet_client.set_time(time)
    block = await devnet_client.get_block(block_number="latest")

    assert block.timestamp == time

    await devnet_client.increase_time(100)
    block = await devnet_client.get_block(block_number="latest")

    assert block.timestamp == time + 100
