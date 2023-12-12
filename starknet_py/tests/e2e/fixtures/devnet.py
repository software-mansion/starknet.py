import os
import socket
import subprocess
import time
from contextlib import closing
from typing import Generator, List

import pytest


def get_available_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]


def start_devnet():
    devnet_port = get_available_port()

    if os.name == "nt":
        start_devnet_command = start_devnet_command_windows(devnet_port)
    else:
        start_devnet_command = start_devnet_command_unix(devnet_port)

    # pylint: disable=consider-using-with
    proc = subprocess.Popen(start_devnet_command)
    time.sleep(10)
    return devnet_port, proc


def start_devnet_command_unix(devnet_port: int) -> List[str]:
    return [
        "starknet-devnet",
        "--port",
        str(devnet_port),
        "--accounts",  # deploys specified number of accounts
        str(1),
        "--seed",  # generates same accounts each time
        str(1),
    ]


def start_devnet_command_windows(devnet_port: int) -> List[str]:
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
