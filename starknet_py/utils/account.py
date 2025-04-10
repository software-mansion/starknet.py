# TODO(#1582): Remove braavos-related code once braavos integration is restored
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ClientError

_BRAAVOS_CLASS_HASHES = [
    0x02C8C7E6FBCFB3E8E15A46648E8914C6AA1FC506FC1E7FB3D1E19630716174BC,
    0x00816DD0297EFC55DC1E7559020A3A825E81EF734B558F03C83325D4DA7E6253,
    0x041BF1E71792AECB9DF3E9D04E1540091C5E13122A731E02BEC588F71DC1A5C3,
]


class BraavosAccountDisabledError(ValueError):
    """Raised when a Braavos account is used but is disabled for compatibility reasons."""


async def _raise_error_for_braavos_account(
    exception: Exception, address: int, client: Client
):
    if isinstance(exception, ClientError) and "INVALID_TX" in exception.message:
        class_hash = await client.get_class_hash_at(address)
        if class_hash in _BRAAVOS_CLASS_HASHES:
            # pylint: disable=line-too-long
            raise BraavosAccountDisabledError(
                "Using Braavos accounts is temporarily disabled because they don't yet work with starknet 0.13.5."
                "Visit this link to read more: https://community.starknet.io/t/starknet-devtools-for-0-13-5/115495#p-2359168-braavos-compatibility-issues-3"
            )
