import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(os.path.dirname(__file__)) / "../test-variables.env")


def _get_env_or_throw(env_name: str) -> str:
    env = os.getenv(key=env_name)
    if env is None:
        raise ValueError(
            f"{env_name} environmental variable is not set. "
            f"Update it manually or set it in `starknet_py/tests/e2e/test-variables.env` file."
        )
    return env


def _get_env_lambda(env_name):
    return lambda: _get_env_or_throw(env_name)


# -------------------------------- TESTNET -------------------------------------

TESTNET_ACCOUNT_ADDRESS = _get_env_lambda("TESTNET_ACCOUNT_ADDRESS")

TESTNET_ACCOUNT_PRIVATE_KEY = _get_env_lambda("TESTNET_ACCOUNT_PRIVATE_KEY")

TESTNET_NODE_URL = _get_env_lambda("TESTNET_NODE_URL")

# -------------------------------- INTEGRATION ---------------------------------

INTEGRATION_ACCOUNT_PRIVATE_KEY = _get_env_lambda("INTEGRATION_ACCOUNT_PRIVATE_KEY")

INTEGRATION_ACCOUNT_ADDRESS = _get_env_lambda("INTEGRATION_ACCOUNT_ADDRESS")

INTEGRATION_NODE_URL = _get_env_lambda("INTEGRATION_NODE_URL")

INTEGRATION_GATEWAY_URL = "https://external.integration.starknet.io"

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

MAX_FEE = int(1e16)

MOCK_DIR = Path(os.path.dirname(__file__)) / "../mock"
TYPED_DATA_DIR = MOCK_DIR / "typed_data"
CONTRACTS_DIR = MOCK_DIR / "contracts"
CONTRACTS_V1_DIR = MOCK_DIR / "contracts_v1"
CONTRACTS_COMPILED_DIR = MOCK_DIR / "contracts_compiled"
CONTRACTS_COMPILED_V1_DIR = MOCK_DIR / "contracts_compiled_v1"
CONTRACTS_COMPILED_V2_DIR = MOCK_DIR / "contracts_compiled_v2"
CONTRACTS_PRECOMPILED_DIR = CONTRACTS_COMPILED_DIR / "precompiled"
ACCOUNT_DIR = MOCK_DIR / "account"
