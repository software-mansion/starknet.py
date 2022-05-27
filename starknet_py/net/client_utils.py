from starknet_py.net.client_models import Hash


def convert_to_felt(value: Hash) -> str:
    """
    Convert hash to hexadecimal string
    """
    if isinstance(value, str):
        return value

    return hex(value)
