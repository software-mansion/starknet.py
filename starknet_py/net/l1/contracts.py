from typing import Sequence, cast, Optional

# noinspection PyProtectedMember
from web3._utils.contracts import prepare_transaction
from web3 import Web3
from web3.types import (
    BlockIdentifier as EthBlockIdentifier,
    ABIFunction,
    ABIFunctionParams,
    TxParams,
)
from eth_typing import (
    ChecksumAddress,
)

from starknet_py.net.models import StarknetChainId


def get_l1_starknet_contract_address(net: StarknetChainId):
    return {
        # Contract Proxy addresses
        StarknetChainId.TESTNET: "0xde29d060D45901Fb19ED6C6e959EB22d8626708e",
        StarknetChainId.MAINNET: "0xc662c410C0ECf747543f5bA90660f6ABeBD9C8c4",
    }[net]


class StarknetL1Contract:
    def __init__(
        self,
        net: StarknetChainId,
        web3: Web3,
    ):
        self.w3 = web3
        self.contract_address: ChecksumAddress = cast(
            ChecksumAddress, get_l1_starknet_contract_address(net)
        )

    def l2_to_l1_messages(
        self, msg_hash: bytes, block_number: Optional[EthBlockIdentifier] = None
    ) -> bytes:
        abi: ABIFunction = {
            "inputs": cast(
                Sequence[ABIFunctionParams],
                [{"internalType": "bytes32", "name": "msgHash", "type": "bytes32"}],
            ),
            "name": "l2ToL1Messages",
            "outputs": cast(
                Sequence[ABIFunctionParams],
                [{"internalType": "uint256", "name": "", "type": "uint256"}],
            ),
            "stateMutability": "view",
            "type": "function",
        }

        return self.w3.eth.call(
            prepare_transaction(
                address=cast(ChecksumAddress, self.contract_address),
                w3=self.w3,
                transaction=cast(TxParams, {"value": 0}),
                fn_identifier="l2ToL1Messages",
                fn_abi=abi,
                fn_args=[msg_hash],
            ),
            block_number,
        )

    def l1_to_l2_messages(
        self, msg_hash: bytes, block_number: Optional[EthBlockIdentifier] = None
    ) -> bytes:
        abi: ABIFunction = {
            "inputs": cast(
                Sequence[ABIFunctionParams],
                [{"internalType": "bytes32", "name": "msgHash", "type": "bytes32"}],
            ),
            "name": "l1ToL2Messages",
            "outputs": cast(
                Sequence[ABIFunctionParams],
                [{"internalType": "uint256", "name": "", "type": "uint256"}],
            ),
            "stateMutability": "view",
            "type": "function",
        }

        return self.w3.eth.call(
            prepare_transaction(
                address=self.contract_address,
                w3=self.w3,
                transaction=cast(TxParams, {"value": 0}),
                fn_identifier="l1ToL2Messages",
                fn_abi=abi,
                fn_args=[msg_hash],
            ),
            block_number,
        )
