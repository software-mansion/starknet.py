from web3._utils.contracts import prepare_transaction
from web3.types import BlockIdentifier
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet

from starknet_py.net.models import StarknetChainId


# pylint: disable=invalid-name
class StarknetL1Contract:
    def __init__(
        self,
        net: StarknetChainId,
        endpoint_uri: str,
    ):
        self.w3 = Web3(
            AsyncHTTPProvider(endpoint_uri),
            modules={"eth": AsyncEth, "net": AsyncNet},
            middlewares=[],
        )
        self.contract_address = {
            # Contract Proxy addresses
            StarknetChainId.TESTNET: "0xde29d060D45901Fb19ED6C6e959EB22d8626708e",
            StarknetChainId.MAINNET: "0xc662c410C0ECf747543f5bA90660f6ABeBD9C8c4",
        }[net]

    async def l2ToL1Messages(
        self, msg_hash: int, block_number: BlockIdentifier = None
    ) -> int:
        abi = {
            "inputs": [
                {"internalType": "bytes32", "name": "msgHash", "type": "bytes32"}
            ],
            "name": "l2ToL1Messages",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        }

        return await self.w3.eth.call(
            prepare_transaction(
                address=self.contract_address,
                web3=self.w3,
                transaction={"value": 0},
                fn_identifier="l2ToL1Messages",
                fn_abi=abi,
                fn_args=[msg_hash],
            ),
            block_number,
        )

    async def l1ToL2Messages(
        self, msg_hash: int, block_number: BlockIdentifier = None
    ) -> int:
        abi = {
            "inputs": [
                {"internalType": "bytes32", "name": "msgHash", "type": "bytes32"}
            ],
            "name": "l1ToL2Messages",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        }

        return await self.w3.eth.call(
            prepare_transaction(
                address=self.contract_address,
                web3=self.w3,
                transaction={"value": 0},
                fn_identifier="l1ToL2Messages",
                fn_abi=abi,
                fn_args=[msg_hash],
            ),
            block_number,
        )
