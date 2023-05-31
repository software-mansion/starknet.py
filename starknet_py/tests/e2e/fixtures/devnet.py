import os
import re
import socket
import subprocess
import time
from contextlib import closing
from pathlib import Path
from typing import Generator, List, Optional

import pytest

from starknet_py.constants import ROOT_PATH


def extract_devnet_version() -> Optional[str]:
    """
    Returns either the version of starknet-devnet from pyproject.toml or None.
    """
    pattern = (
        r"""starknet-devnet\s*=\s*{[^}]*?\bversion\s*=\s*["']\D*(\d+(?:\.\d+)+)["']"""
    )

    with open(ROOT_PATH / "../pyproject.toml", encoding="utf-8") as pyproject_toml:
        match = re.search(pattern, str(pyproject_toml))
        return None if match is None else match[0]


def get_available_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]


def get_compiler_manifest() -> List[str]:
    """
    Load manifest-path file and return it as --cairo-compiler-manifest flag to starknet-devnet.
    To configure manifest locally, install Cairo 1 compiler https://github.com/starkware-libs/cairo
    and create manifest-path containing a path to top-level Cargo.toml file in cairo 1 compiler directory
    file from manifest-path.template.
    """
    try:
        manifest_file_path = Path(os.path.dirname(__file__)) / "../manifest-path"
        manifest = manifest_file_path.read_text("utf-8").splitlines()[0]

        return ["--cairo-compiler-manifest", manifest]
    except (IndexError, FileNotFoundError):
        return []


def start_devnet():
    devnet_port = get_available_port()
    devnet_version = extract_devnet_version() or "latest"

    if os.name == "nt":
        start_devnet_command = start_devnet_command_windows(devnet_port, devnet_version)
    else:
        start_devnet_command = start_devnet_command_unix(devnet_port)

    # pylint: disable=consider-using-with
    proc = subprocess.Popen(start_devnet_command)
    time.sleep(10)
    return devnet_port, proc


def start_devnet_command_unix(devnet_port: int) -> List[str]:
    return [
        "poetry",
        "run",
        "starknet-devnet",
        "--host",
        "localhost",
        "--port",
        str(devnet_port),
        "--accounts",  # deploys specified number of accounts
        str(1),
        "--seed",  # generates same accounts each time
        str(1),
        *get_compiler_manifest(),
    ]


def start_devnet_command_windows(devnet_port: int, devnet_version: str) -> List[str]:
    return [
        "wsl",
        "python3",
        "-m",
        "starknet_devnet.server",
        "--port",
        f"{devnet_port}",
        "--accounts",
        str(1),
        "--seed",
        str(1),
    ]


@pytest.fixture(scope="package")
def run_devnet() -> Generator[str, None, None]:
    """
    Runs devnet instance once per module and returns it's address.
    """
    devnet_port, proc = start_devnet()
    yield f"http://localhost:{devnet_port}"
    proc.kill()
