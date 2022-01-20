from web3 import Web3
from web3.contract import Contract as Web3Contract
from web3.providers import BaseProvider as L1Provider

from starknet_py.net.l1.networks import L1Network
from starknet_py.net.l1.starknet_core_abi import STARKNET_CORE_L1_ABI


class StarknetL1Contract:
    @staticmethod
    def on_l1_net(l1_net: L1Network, l1_net_provider: L1Provider) -> Web3Contract:
        w3 = Web3(l1_net_provider)
        return w3.eth.contract(
            address=StarknetL1Contract.address_from_l1_net(l1_net),
            abi=STARKNET_CORE_L1_ABI,
        )

    @staticmethod
    def address_from_l1_net(l1_net: L1Network) -> str:
        return {
            # Contract Proxy addresses
            L1Network.GOERLI_TESTNET: "0xde29d060D45901Fb19ED6C6e959EB22d8626708e",
            L1Network.MAINNET: "0xc662c410C0ECf747543f5bA90660f6ABeBD9C8c4",
        }[l1_net]
