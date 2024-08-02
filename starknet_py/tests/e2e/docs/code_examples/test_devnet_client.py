# pylint: disable=unused-variable
from starknet_py.devnet_utils.devnet_client import DevnetClient


def test_init():
    # docs-start: init
    client = DevnetClient(node_url="https://your.node.url")
    # docs-end: init
