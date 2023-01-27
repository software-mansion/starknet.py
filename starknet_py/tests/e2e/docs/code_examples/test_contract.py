# pylint: disable=unused-variable
from starknet_py.contract import Contract
from starknet_py.net import KeyPair
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import TESTNET


def test_init():
    # docs-start: init
    contract = Contract(
        address=0x123,
        abi=[
            {
                "inputs": [{"name": "amount", "type": "felt"}],
                "name": "increase_balance",
                "outputs": [],
                "type": "function",
            },
        ],
        provider=Account(
            address=0x321,
            client=GatewayClient(TESTNET),
            key_pair=KeyPair(12, 34),
            chain=StarknetChainId.TESTNET,
        ),
    )
    # docs-end: init
