from starknet_py.net.full_node_client import FullNodeClient


def test_synchronous_full_node_client():
    # pylint: disable=no-member, unused-variable
    # docs: start
    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(node_url=node_url)

    call_result = full_node_client.get_block_sync(block_number=1)
    # docs: end
