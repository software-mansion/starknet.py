import json
from pathlib import Path
from typing import Optional, Tuple, Union
from starknet_py.common import create_casm_class, create_sierra_compiled_contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.tests.e2e.fixtures.misc import UnknownArtifacts


def _extract_compiled_class_hash(
    compiled_contract_casm: Optional[str] = None,
    compiled_class_hash: Optional[int] = None,
) -> int:
    if compiled_class_hash is None and compiled_contract_casm is None:
        raise ValueError(
            "For Cairo 1.0 contracts, either the 'compiled_class_hash' or the 'compiled_contract_casm' "
            "argument must be provided."
        )

    if compiled_class_hash is None:
        assert compiled_contract_casm is not None
        compiled_class_hash = compute_casm_class_hash(
            create_casm_class(compiled_contract_casm)
        )

    return compiled_class_hash


def _unpack_provider(
    provider: Union[BaseAccount, Client]
) -> Tuple[Client, Optional[BaseAccount]]:
    """
    Get the client and optional account to be used by Contract.

    If provided with Client, returns this Client and None.
    If provided with BaseAccount, returns underlying Client and the account.
    """
    if isinstance(provider, Client):
        return provider, None

    if isinstance(provider, BaseAccount):
        return provider.client, provider

    raise ValueError("Argument provider is not of accepted type.")

def load_contract(contract_name: str, package_name: str, binaries_directory_path: str = "target/dev"):
    """
    Load and return the contract's CASM, Sierra, and ABI information.

    Args:
        contract_name (str): The name of the contract to be loaded.
        package_name (str): The name of the Scarb package containing the contract.
        binaries_directory_path (str, optional): The directory path to the Scarb-compiled binaries. 
                                                 Defaults to "target/dev" relative to the working directory.

    Returns:
        dict: A dictionary with the following keys:
            - "casm" (str): CASM (Cairo Assembly) representation of the contract.
            - "sierra" (str): Sierra intermediate representation of the contract.
            - "abi" (list): ABI (Application Binary Interface) of the contract.
    """
    # Define the base directory for the compiled contracts
    base_dir = Path(binaries_directory_path)
    # Create the path for the artifacts map file using pathlib
    artifacts_map_path = base_dir / f"{package_name}.starknet_artifacts.json"
    # Read the content of the JSON file using read_text method of the Path object
    artifacts_map = json.loads(artifacts_map_path.read_text("utf-8"))
    artifact_file_names = next(
        (
            item["artifacts"]
            for item in artifacts_map["contracts"]
            if item["contract_name"] == contract_name
        ),
        None,
    )

    if not isinstance(artifact_file_names, dict):  # pyright: ignore
        raise UnknownArtifacts(f"Artifacts for contract {contract_name} not found")

    sierra = (base_dir / artifact_file_names["sierra"]).read_text("utf-8")
    casm = (base_dir / artifact_file_names["casm"]).read_text("utf-8")
    abi = create_sierra_compiled_contract(sierra).parsed_abi
    return {"casm": casm, "sierra": sierra, "abi": abi}
