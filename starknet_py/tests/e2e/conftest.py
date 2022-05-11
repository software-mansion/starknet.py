import time
import subprocess
import socket
from contextlib import closing

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--net",
        action="store",
        default="devnet",
        help="Network to run tests on: possible 'testnet', 'devnet'",
    )


def get_available_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]


def start_devnet():
    devnet_port = get_available_port()

    command = [
        "poetry",
        "run",
        "starknet-devnet",
        "--host",
        "localhost",
        "--port",
        str(devnet_port),
    ]
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(command)
    time.sleep(5)
    return devnet_port, proc


@pytest.fixture(scope="module", autouse=True)
def run_devnet(request):
    net = request.config.getoption("--net")
    if net == "devnet":
        devnet_port, proc = start_devnet()
        yield f"http://localhost:{devnet_port}"
        proc.kill()
    elif net == "testnet":
        yield "testnet"
    else:
        raise ValueError("Not supported value provided for --net")


@pytest.fixture
def run_net(request):
    return request.config.getoption("--net")
