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


# -------------------------------- SEPOLIA TESTNET -------------------------------------

SEPOLIA_ACCOUNT_PRIVATE_KEY = _get_env_lambda("SEPOLIA_ACCOUNT_PRIVATE_KEY")

SEPOLIA_ACCOUNT_ADDRESS = _get_env_lambda("SEPOLIA_ACCOUNT_ADDRESS")

SEPOLIA_RPC_URL = _get_env_lambda("SEPOLIA_RPC_URL")

EMPTY_CONTRACT_ADDRESS_SEPOLIA = (
    "0x06524771cb912945bf2db355b5a12355ca2e2ff05e15ee35366336a602293f2d"
)

# -----------------------------------------------------------------------------

DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS = (
    "0x260a8311b4f1092db620b923e8d7d20e76dedcc615fb4b6fdf28315b81de201"
)
DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY = "0xc10662b7b247c7cecf7e8a30726cff12"

STRK_FEE_CONTRACT_ADDRESS = (
    "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
)

STRK_CLASS_HASH = "0x04ad3c1dc8413453db314497945b6903e1c766495a1e60492d44da9c2a986e4b"

MAX_RESOURCE_BOUNDS_L1 = ResourceBounds(
    max_amount=int(1e5), max_price_per_unit=int(1e13)
)

MAX_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    l2_gas=ResourceBounds(max_amount=int(1e10), max_price_per_unit=int(1e20)),
    l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
)

MAX_RESOURCE_BOUNDS_SEPOLIA = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=int(1e4), max_price_per_unit=int(1e15)),
    l2_gas=ResourceBounds(max_amount=int(1e6), max_price_per_unit=int(1e10)),
    l1_data_gas=ResourceBounds(max_amount=int(1e4), max_price_per_unit=int(1e15)),
)

MOCK_DIR = Path(os.path.dirname(__file__)) / "../mock"
TYPED_DATA_DIR = MOCK_DIR / "typed_data"
CONTRACTS_DIR = MOCK_DIR / "contracts"
CONTRACTS_COMPILED_V0_DIR = MOCK_DIR / "contracts_compiled"
CAIRO_0_CONTRACTS_ABI_DIR = MOCK_DIR / "cairo_0_contracts_abi"


# PRECOMPILED_CONTRACTS are contracts compiled with various Sierras
# They are mainly used to verify if we compute class_hash for older Sierras correctly
PRECOMPILED_CONTRACTS_DIR = MOCK_DIR / "precompiled_contracts"

CONTRACTS_V2_COMPILED = MOCK_DIR / "contracts_v2/target/dev"
CONTRACTS_V2_ARTIFACTS_MAP = (
    CONTRACTS_V2_COMPILED / "contracts_v2.starknet_artifacts.json"
)

CONTRACTS_V1_COMPILED = MOCK_DIR / "contracts_v1/target/dev"
CONTRACTS_V1_ARTIFACTS_MAP = (
    CONTRACTS_V1_COMPILED / "contracts_v1.starknet_artifacts.json"
)
