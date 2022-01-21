from web3 import Web3
from web3.contract import Contract as Web3Contract

from starknet_py.net.l1.starknet_core_abi import STARKNET_CORE_L1_ABI
from starknet_py.net.models import StarknetChainId


class StarknetL1Contract:
    @staticmethod
    def on_l1_net(net: StarknetChainId, w3: Web3) -> Web3Contract:
        return w3.eth.contract(
            address=StarknetL1Contract.address_from_l1_net(net),
            abi=STARKNET_CORE_L1_ABI,
        )

    @staticmethod
    def address_from_l1_net(net: StarknetChainId) -> str:
        return {
            # Contract Proxy addresses
            StarknetChainId.TESTNET: "0xde29d060D45901Fb19ED6C6e959EB22d8626708e",
            StarknetChainId.MAINNET: "0xc662c410C0ECf747543f5bA90660f6ABeBD9C8c4",
        }[net]
