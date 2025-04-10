# TODO(#1582): Remove this test once braavos integration is restored
import pytest

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    SEPOLIA_BRAAVOS_ACCOUNT_ADDRESS,
    SEPOLIA_BRAAVOS_ACCOUNT_PRIVATE_KEY,
)
from starknet_py.utils.account import BraavosAccountDisabledError


@pytest.mark.asyncio
async def test_account_execute_v3_braavos(client_sepolia_testnet: FullNodeClient):
    braavos_account = Account(
        address=SEPOLIA_BRAAVOS_ACCOUNT_ADDRESS(),
        client=client_sepolia_testnet,
        chain=StarknetChainId.SEPOLIA,
        key_pair=KeyPair.from_private_key(SEPOLIA_BRAAVOS_ACCOUNT_PRIVATE_KEY()),
    )
    with pytest.raises(BraavosAccountDisabledError):
        await braavos_account.execute_v3(
            calls=[
                Call(
                    to_addr=0x0589A8B8BF819B7820CB699EA1F6C409BC012C9B9160106DDC3DACD6A89653CF,
                    selector=get_selector_from_name("get_balance"),
                    calldata=[],
                )
            ],
            auto_estimate=True,
        )
