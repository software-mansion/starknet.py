import pytest

from starknet_py.net import Client
from starknet_py.net.networks import TESTNET


@pytest.mark.asyncio
def test_synchronous_testnet_client():
    synchronous_testnet_client = Client(TESTNET)
    # pylint: disable=no-member, unused-variable
    call_result = synchronous_testnet_client.get_block_sync(
        "0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943"
    )
