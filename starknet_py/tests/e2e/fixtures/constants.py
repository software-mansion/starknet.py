import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(os.path.dirname(__file__)) / "../test-variables.env")


def _get_env_or_throw(env_name: str) -> str:
    env = os.getenv(key=env_name)
    if env is None:
        raise ValueError(
            f"{env_name} environmental variable is not set. "
            f"Update it manually or set it in `starknet_py/tests/e2e/test-variables.env` file. "
            f"More info here: https://starknetpy.readthedocs.io/en/latest/development.html#setup"
        )
    return env


def _get_env_lambda(env_name):
    return lambda: _get_env_or_throw(env_name)


# -------------------------------- TESTNET -------------------------------------

TESTNET_ACCOUNT_ADDRESS = _get_env_lambda("TESTNET_ACCOUNT_ADDRESS")

TESTNET_ACCOUNT_PRIVATE_KEY = _get_env_lambda("TESTNET_ACCOUNT_PRIVATE_KEY")

TESTNET_RPC_URL = _get_env_lambda("TESTNET_RPC_URL")

EMPTY_CONTRACT_ADDRESS_TESTNET = (
    "0x01de0e8ec5303c4624b96733bed7e4261724df4aecedae6305efa35931a4f0e6"
)

# -------------------------------- INTEGRATION ---------------------------------

INTEGRATION_ACCOUNT_PRIVATE_KEY = _get_env_lambda("INTEGRATION_ACCOUNT_PRIVATE_KEY")

INTEGRATION_ACCOUNT_ADDRESS = _get_env_lambda("INTEGRATION_ACCOUNT_ADDRESS")

INTEGRATION_RPC_URL = _get_env_lambda("INTEGRATION_RPC_URL")

EMPTY_CONTRACT_ADDRESS_INTEGRATION = (
    "0x0751cb46C364E912b6CB9221A857D8f90B1F6995A0e902997df774631432970E"
)

MAP_CONTRACT_ADDRESS_INTEGRATION = (
    "0x05cd21d6b3952a869fda11fa9a5bd2657bd68080d3da255655ded47a81c8bd53"
)

# -----------------------------------------------------------------------------

DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS = (
    "0x260a8311b4f1092db620b923e8d7d20e76dedcc615fb4b6fdf28315b81de201"
)
DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY = "0xc10662b7b247c7cecf7e8a30726cff12"

DEVNET_PATH = _get_env_lambda("DEVNET_PATH")

MAX_FEE = int(1e16)

MOCK_DIR = Path(os.path.dirname(__file__)) / "../mock"
TYPED_DATA_DIR = MOCK_DIR / "typed_data"
CONTRACTS_DIR = MOCK_DIR / "contracts"
CONTRACTS_V1_DIR = MOCK_DIR / "contracts_v1"
CONTRACTS_COMPILED_V0_DIR = MOCK_DIR / "contracts_compiled"
CONTRACTS_COMPILED_V1_DIR = MOCK_DIR / "contracts_compiled_v1"
CONTRACTS_COMPILED_V2_DIR = MOCK_DIR / "contracts_compiled_v2"
CONTRACTS_PRECOMPILED_DIR = CONTRACTS_COMPILED_V0_DIR / "precompiled"
ACCOUNT_DIR = MOCK_DIR / "account"
