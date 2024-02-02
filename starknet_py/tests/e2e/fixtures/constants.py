import os
from pathlib import Path

from dotenv import load_dotenv

from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping

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


# -------------------------------- GOERLI TESTNET -------------------------------------

GOERLI_TESTNET_ACCOUNT_ADDRESS = _get_env_lambda("GOERLI_TESTNET_ACCOUNT_ADDRESS")

GOERLI_TESTNET_ACCOUNT_PRIVATE_KEY = _get_env_lambda(
    "GOERLI_TESTNET_ACCOUNT_PRIVATE_KEY"
)

GOERLI_TESTNET_RPC_URL = _get_env_lambda("GOERLI_TESTNET_RPC_URL")

EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET = (
    "0x01de0e8ec5303c4624b96733bed7e4261724df4aecedae6305efa35931a4f0e6"
)

# -------------------------------- GOERLI INTEGRATION ---------------------------------

GOERLI_INTEGRATION_ACCOUNT_PRIVATE_KEY = _get_env_lambda(
    "GOERLI_INTEGRATION_ACCOUNT_PRIVATE_KEY"
)

GOERLI_INTEGRATION_ACCOUNT_ADDRESS = _get_env_lambda(
    "GOERLI_INTEGRATION_ACCOUNT_ADDRESS"
)

GOERLI_INTEGRATION_RPC_URL = _get_env_lambda("GOERLI_INTEGRATION_RPC_URL")

EMPTY_CONTRACT_ADDRESS_GOERLI_INTEGRATION = (
    "0x0751cb46C364E912b6CB9221A857D8f90B1F6995A0e902997df774631432970E"
)

MAP_CONTRACT_ADDRESS_GOERLI_INTEGRATION = (
    "0x05cd21d6b3952a869fda11fa9a5bd2657bd68080d3da255655ded47a81c8bd53"
)

# -------------------------------- SEPOLIA TESTNET -------------------------------------

SEPOLIA_TESTNET_ACCOUNT_PRIVATE_KEY = _get_env_lambda(
    "SEPOLIA_TESTNET_ACCOUNT_PRIVATE_KEY"
)

SEPOLIA_TESTNET_ACCOUNT_ADDRESS = _get_env_lambda("SEPOLIA_TESTNET_ACCOUNT_ADDRESS")

SEPOLIA_TESTNET_RPC_URL = _get_env_lambda("SEPOLIA_TESTNET_RPC_URL")

# -------------------------------- SEPOLIA INTEGRATION -------------------------------------

SEPOLIA_INTEGRATION_ACCOUNT_PRIVATE_KEY = _get_env_lambda(
    "SEPOLIA_INTEGRATION_ACCOUNT_PRIVATE_KEY"
)

SEPOLIA_INTEGRATION_ACCOUNT_ADDRESS = _get_env_lambda(
    "SEPOLIA_INTEGRATION_ACCOUNT_ADDRESS"
)

SEPOLIA_INTEGRATION_RPC_URL = _get_env_lambda("SEPOLIA_INTEGRATION_RPC_URL")

# -----------------------------------------------------------------------------

DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS = (
    "0x260a8311b4f1092db620b923e8d7d20e76dedcc615fb4b6fdf28315b81de201"
)
DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY = "0xc10662b7b247c7cecf7e8a30726cff12"

STRK_FEE_CONTRACT_ADDRESS = (
    "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
)

MAX_FEE = int(1e16)

MAX_RESOURCE_BOUNDS_L1 = ResourceBounds(max_amount=5000, max_price_per_unit=int(2e12))
MAX_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=MAX_RESOURCE_BOUNDS_L1, l2_gas=ResourceBounds.init_with_zeros()
)

MOCK_DIR = Path(os.path.dirname(__file__)) / "../mock"
TYPED_DATA_DIR = MOCK_DIR / "typed_data"
CONTRACTS_DIR = MOCK_DIR / "contracts"
CONTRACTS_V1_DIR = MOCK_DIR / "contracts_v1"
CONTRACTS_COMPILED_V0_DIR = MOCK_DIR / "contracts_compiled"
CONTRACTS_COMPILED_V1_DIR = MOCK_DIR / "contracts_compiled_v1"
CONTRACTS_COMPILED_V2_DIR = MOCK_DIR / "contracts_compiled_v2"
CONTRACTS_PRECOMPILED_DIR = CONTRACTS_COMPILED_V0_DIR / "precompiled"
ACCOUNT_DIR = MOCK_DIR / "account"
