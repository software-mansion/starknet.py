from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.networks import TESTNET


def test_synchronous_gateway_client():
    # pylint: disable=no-member, unused-variable
    # docs: start
    synchronous_testnet_client = GatewayClient(TESTNET)
    call_result = synchronous_testnet_client.get_block_sync(
        "0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943"
    )
    # docs: end
