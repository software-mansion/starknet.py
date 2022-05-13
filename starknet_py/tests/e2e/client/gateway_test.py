import pytest

from starknet_py.net.base_client import BlockNumberIdentifier
from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_gateway_get_transaction_throws_on_non_int_identifier(
    devnet_address, deploy_transaction_hash
):
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    identifier: BlockNumberIdentifier = {"block_number": 0, "index": 0}

    with pytest.raises(ValueError) as exinfo:
        await client.get_transaction(tx_identifier=identifier)

    assert (
        "BlockHashIdentifier and BlockNumberIdentifier are not supported in gateway client."
        in str(exinfo.value)
    )
