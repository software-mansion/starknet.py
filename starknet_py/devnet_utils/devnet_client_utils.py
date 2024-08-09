import re

from starknet_py.net.client_models import Hash


def _to_eth_address(value: Hash) -> str:
    """
    Convert the value to Ethereum address matching a ``^0x[a-fA-F0-9]{40}$`` pattern.

    :param value: The value to convert.
    :return: Ethereum address representation of the value.
    """
    if isinstance(value, str):
        value = int(value, 16)

    eth_address = f"0x{value:040x}"
    assert re.match("^0x[a-fA-F0-9]{40}$", eth_address)
    return eth_address
