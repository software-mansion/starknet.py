import pytest


@pytest.mark.asyncio
async def test_time_advancing(devnet_client):
    time = 3384617820
    await devnet_client.set_time(time, generate_block=True)
    block = await devnet_client.get_block(block_number="latest")

    assert block.timestamp == time

    await devnet_client.increase_time(100)
    block = await devnet_client.get_block(block_number="latest")

    assert block.timestamp == time + 100


@pytest.mark.asyncio
async def test_time_set_with_generate_block(devnet_client):
    time = 3384617820

    block_number_before = await devnet_client.get_block_number()
    await devnet_client.set_time(time, generate_block=True)
    block_number_after = await devnet_client.get_block_number()

    assert block_number_after == block_number_before + 1


@pytest.mark.asyncio
async def test_time_set_without_generate_block(devnet_client):
    time = 3384617820

    block_number_before = await devnet_client.get_block_number()
    await devnet_client.set_time(time, generate_block=False)
    block_number_after = await devnet_client.get_block_number()

    assert block_number_after == block_number_before
