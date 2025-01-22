import pytest

from starknet_py.net.client_models import (
    ResourceBoundsMapping,
    StarknetBlock,
    Transaction,
)


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_using_full_node_client(client, map_contract):
    # pylint: disable=import-outside-toplevel, unused-variable
    full_node_client_fixture = client

    # docs: start
    from starknet_py.net.client_models import ResourceBounds
    from starknet_py.net.full_node_client import FullNodeClient

    node_url = "https://your.node.url"
    client = FullNodeClient(node_url=node_url)
    # docs: end

    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    )
    await map_contract.functions["put"].prepare_invoke_v3(key=10, value=10).invoke(
        resource_bounds=resource_bounds
    )

    client = full_node_client_fixture
    # docs: start

    call_result = await client.get_block(block_number=1)
    # docs: end
    assert isinstance(call_result, StarknetBlock)
    assert len(call_result.transactions) == 1
    assert isinstance(call_result.transactions[0], Transaction)
    assert call_result.block_hash
