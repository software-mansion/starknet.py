import pytest

from starknet_py.net.client_models import TransactionStatusResponse, TransactionStatus
from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_gateway_raises_on_both_block_hash_and_number(
    devnet_address, block_with_deploy_hash
):
    client = DevnetClientFactory(devnet_address).make_devnet_client_without_account()

    with pytest.raises(ValueError) as exinfo:
        await client.get_block(block_hash=block_with_deploy_hash, block_number=0)

    assert "Block_hash and block_number parameters are mutually exclusive" in str(
        exinfo.value
    )


@pytest.mark.asyncio
async def test_get_class_hash_at(devnet_address, contract_address):
    client = DevnetClientFactory(devnet_address).make_devnet_client_without_account()

    class_hash = await client.get_class_hash_at(contract_address=contract_address)

    assert (
        class_hash
        == 3197248528421459336430560285234479619486870042069853528940753151314137720584
    )


@pytest.mark.asyncio
async def test_get_code(devnet_address, contract_address):
    client = DevnetClientFactory(devnet_address).make_devnet_client_without_account()
    code = await client.get_code(contract_address=contract_address)

    assert code.abi is not None
    assert len(code.abi) != 0
    assert code.bytecode is not None
    assert len(code.bytecode) != 0


@pytest.mark.asyncio
async def test_get_transaction_status(devnet_address, invoke_transaction_hash):
    client = DevnetClientFactory(devnet_address).make_devnet_client_without_account()
    tx_status_resp = await client.get_transaction_status(invoke_transaction_hash)
    assert isinstance(tx_status_resp, TransactionStatusResponse)
    assert tx_status_resp.transaction_status == TransactionStatus.ACCEPTED_ON_L2
    assert isinstance(tx_status_resp.block_hash, int)
