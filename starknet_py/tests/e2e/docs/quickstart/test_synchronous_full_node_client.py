from starknet_py.net.full_node_client import FullNodeClient


def test_synchronous_gateway_client():
    # pylint: disable=no-member, unused-variable
    # docs: start
    node_url = "https://your.node.url"
    synchronous_full_node_client = FullNodeClient(node_url=node_url)
    # docs: end

    synchronous_full_node_client = FullNodeClient(
        node_url="http://188.34.188.184:9545/rpc/v0.3"
    )

    # docs: start
    call_result = synchronous_full_node_client.get_block_sync(block_number=1)
    # docs: end
