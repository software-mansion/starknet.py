from starknet_py.net.full_node_client import FullNodeClient


def test_synchronous_full_node_client(
    full_node_client,
    map_contract_declare_hash,  # pylint: disable=unused-argument
):
    # pylint: disable=unused-variable
    fixture_client = full_node_client

    # docs: start
    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(node_url=node_url)
    # docs: end

    full_node_client = fixture_client

    # docs: start
    call_result = full_node_client.get_block_sync(block_number=1)
    # docs: end
