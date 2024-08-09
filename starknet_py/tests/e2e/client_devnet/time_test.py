import pytest


@pytest.mark.asyncio
async def test_set_and_increase_time(devnet_client):
    time = 3384617820
    increase_value, error_margin = 100, 10

    await devnet_client.set_time(time, generate_block=True)
    block = await devnet_client.get_block(block_number="latest")

    assert block.timestamp == time

    await devnet_client.increase_time(increase_value)
    block = await devnet_client.get_block(block_number="latest")

    assert (
        time + increase_value <= block.timestamp <= time + increase_value + error_margin
    )


@pytest.mark.asyncio
async def test_set_time_with_generate_block(devnet_client):
    time = 3384617820

    block_number_before = await devnet_client.get_block_number()
    await devnet_client.set_time(time, generate_block=True)
    block_number_after = await devnet_client.get_block_number()

    assert block_number_after == block_number_before + 1


@pytest.mark.asyncio
async def test_set_time_without_generate_block(devnet_client):
    time = 3384617820

    block_number_before = await devnet_client.get_block_number()
    await devnet_client.set_time(time, generate_block=False)
    block_number_after = await devnet_client.get_block_number()

    assert block_number_after == block_number_before
