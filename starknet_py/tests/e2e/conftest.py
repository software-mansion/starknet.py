import time
import pytest
import subprocess
import os
import socket
from contextlib import closing


def get_available_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="module", autouse=True)
def run_devnet():
    devnet_port = get_available_port()
    os.environ["DEVNET_PORT"] = str(devnet_port)

    command = [
        "poetry",
        "run",
        "starknet-devnet",
        "--host",
        "localhost",
        "--port",
        str(devnet_port),
    ]
    proc = subprocess.Popen(command)
    time.sleep(5)
    yield devnet_port
    proc.kill()
