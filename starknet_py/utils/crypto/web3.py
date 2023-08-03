import re


def is_valid_eth_address(address: str) -> bool:
    """
    A function checking if an address matches Ethereum address regex. Note that it doesn't validate any checksums etc.
    """
    return bool(re.match("^0x[a-fA-F0-9]{40}$", address))
