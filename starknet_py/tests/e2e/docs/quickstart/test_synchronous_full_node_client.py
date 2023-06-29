from starknet_py.net.full_node_client import FullNodeClient


def test_synchronous_full_node_client(full_node_client, map_contract, account):
    # pylint: disable=no-member, unused-variable
    fixture_client = full_node_client

    # docs: start
    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(node_url=node_url)
    # docs: end

    # pylint: disable=import-outside-toplevel
    from starknet_py.contract import Contract

    full_node_client = fixture_client
    key = 1234
    contract = Contract.from_address_sync(
        address=map_contract.address, provider=account
    )
    invocation = contract.functions["put"].invoke_sync(key, 7, max_fee=int(1e16))
    invocation.wait_for_acceptance_sync()

    # docs: start
    call_result = full_node_client.get_block_sync(block_number=1)
    # docs: end
