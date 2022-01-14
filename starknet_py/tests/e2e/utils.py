from starknet_py.net import Client


class DevnetClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__("http://localhost:5000", chain="goerli", *args, **kwargs)
