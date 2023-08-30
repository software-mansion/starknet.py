import os
from pathlib import Path

# -------------------------------- TESTNET -------------------------------------

TESTNET_ACCOUNT_PRIVATE_KEY = (
    "0x61910356c5adf66efb65ec3df5d07a6e5e6e7c8b59f15a13eda7a34c8d1ecc4"
)
TESTNET_ACCOUNT_ADDRESS = (
    "0x59083382aadec25d7616a7f48942d72d469b0ac581f2e935ec26b68f66bd600"
)

# -------------------------------- INTEGRATION ---------------------------------

INTEGRATION_ACCOUNT_PRIVATE_KEY = "0x1234"

INTEGRATION_ACCOUNT_ADDRESS = (
    "0x4321647559947e9109acecb329e57594bcc3981a6118bbbfeaa9f698874bcd5"
)

INTEGRATION_NODE_URL = "http://188.34.188.184:9545/rpc/v0.4"

INTEGRATION_GATEWAY_URL = "https://external.integration.starknet.io"

TESTNET_NODE_URL = "http://188.34.188.184:6060"

PREDEPLOYED_EMPTY_CONTRACT_ADDRESS = (
    "0x0751cb46C364E912b6CB9221A857D8f90B1F6995A0e902997df774631432970E"
)

PREDEPLOYED_MAP_CONTRACT_ADDRESS = (
    "0x05cd21d6b3952a869fda11fa9a5bd2657bd68080d3da255655ded47a81c8bd53"
)

# -----------------------------------------------------------------------------

DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS = (
    "0x7d2f37b75a5e779f7da01c22acee1b66c39e8ba470ee5448f05e1462afcedb4"
)
DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY = "0xcd613e30d8f16adf91b7584a2265b1f5"

MAX_FEE = int(1e20)

MOCK_DIR = Path(os.path.dirname(__file__)) / "../mock"
TYPED_DATA_DIR = MOCK_DIR / "typed_data"
CONTRACTS_DIR = MOCK_DIR / "contracts"
CONTRACTS_V1_DIR = MOCK_DIR / "contracts_v1"
CONTRACTS_COMPILED_DIR = MOCK_DIR / "contracts_compiled"
CONTRACTS_COMPILED_V1_DIR = MOCK_DIR / "contracts_compiled_v1"
CONTRACTS_COMPILED_V2_DIR = MOCK_DIR / "contracts_compiled_v2"
CONTRACTS_PRECOMPILED_DIR = CONTRACTS_COMPILED_DIR / "precompiled"
ACCOUNT_DIR = MOCK_DIR / "account"
