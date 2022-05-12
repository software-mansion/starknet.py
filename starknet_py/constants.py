import os
from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionStatus,
)

TxStatus = TransactionStatus

ACCEPTED_STATUSES = (TxStatus.ACCEPTED_ON_L1, TxStatus.ACCEPTED_ON_L2)

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "."))
DEFAULT_CPP_LIB_PATH = os.path.join(ROOT_DIR, "utils", "crypto")

MAINNET_ETH_CONTRACT = "0xc662c410C0ECf747543f5bA90660f6ABeBD9C8c4"
TESTNET_ETH_CONTRACT = "0xde29d060D45901Fb19ED6C6e959EB22d8626708e"
