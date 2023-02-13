from enum import Enum

from starknet_py.common import int_from_bytes


class StarknetChainId(Enum):
    MAINNET = int_from_bytes(b"SN_MAIN")
    TESTNET = int_from_bytes(b"SN_GOERLI")
    TESTNET2 = int_from_bytes(b"SN_GOERLI2")
