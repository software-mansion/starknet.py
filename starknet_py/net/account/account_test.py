from unittest.mock import patch, AsyncMock

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import KeyPair
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId, parse_address
from starknet_py.net.networks import TESTNET, MAINNET


def test_contract_raises_on_no_client_and_account():
    with pytest.raises(ValueError) as exinfo:
        Contract(address=1234, abi=[])

    assert "One of client or account must be provided" in str(exinfo.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("net", (TESTNET, MAINNET))
async def test_get_balance_default_token_address(net):
    client = GatewayClient(net=net)
    acc_client = Account(
        client=client,
        address="0x123",
        key_pair=KeyPair(123, 456),
        chain=StarknetChainId.TESTNET,
    )

    with patch(
        "starknet_py.net.gateway_client.GatewayClient.call_contract",
        AsyncMock(),
    ) as mocked_call_contract:
        mocked_call_contract.return_value = [0, 0]

        await acc_client.get_balance()

        call = mocked_call_contract.call_args

    (call,) = call[0]

    assert call.to_addr == parse_address(FEE_CONTRACT_ADDRESS)
