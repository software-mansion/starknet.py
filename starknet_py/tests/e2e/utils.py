import os

from starknet_py.net import Client


DEVNET_PORT = os.environ.get("DEVNET_PORT")
if not DEVNET_PORT:
    raise RuntimeError("DEVNET_PORT environment variable not provided!")

DEVNET_ADDRESS = f"http://localhost:{DEVNET_PORT}"


class DevnetClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(DEVNET_ADDRESS, chain="goerli", *args, **kwargs)
