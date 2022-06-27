import pytest

from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_gateway_raises_on_both_block_hash_and_number(
    devnet_address, block_with_deploy_hash
):
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()

    with pytest.raises(ValueError) as exinfo:
        await client.get_block(block_hash=block_with_deploy_hash, block_number=0)

    assert "Block_hash and block_number parameters are mutually exclusive" in str(
        exinfo.value
    )


@pytest.mark.asyncio
async def test_get_class_hash_at(devnet_address, contract_address):
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()

    class_hash = await client.get_class_hash_at(contract_address=contract_address)

    assert (
        class_hash
        == 3197248528421459336430560285234479619486870042069853528940753151314137720584
    )
