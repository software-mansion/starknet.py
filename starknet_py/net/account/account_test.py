from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net import KeyPair
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId, parse_address
from starknet_py.net.networks import MAINNET, TESTNET, TESTNET2
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner


@pytest.mark.asyncio
@pytest.mark.parametrize("net", (TESTNET, TESTNET2, MAINNET))
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


def test_create_account():
    key_pair = KeyPair.from_private_key(0x111)
    account = Account(
        address=0x1,
        client=GatewayClient(net=TESTNET),
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
    )

    assert account.address == 0x1
    assert account.signer.public_key == key_pair.public_key


def test_create_account_from_signer():
    signer = StarkCurveSigner(
        account_address=0x1,
        key_pair=KeyPair.from_private_key(0x111),
        chain_id=StarknetChainId.TESTNET,
    )
    account = Account(address=0x1, client=GatewayClient(net=TESTNET), signer=signer)

    assert account.address == 0x1
    assert account.signer == signer


def test_create_account_raises_on_no_chain_and_signer():
    with pytest.raises(ValueError, match="One of chain or signer must be provided"):
        Account(
            address=0x1,
            client=GatewayClient(net=TESTNET),
            key_pair=KeyPair.from_private_key(0x111),
        )


def test_create_account_raises_on_no_keypair_and_signer():
    with pytest.raises(
        ValueError,
        match="Either a signer or a key_pair must be provided in Account constructor",
    ):
        Account(
            address=0x1,
            client=GatewayClient(net=TESTNET),
            chain=StarknetChainId.TESTNET,
        )


def test_create_account_raises_on_both_keypair_and_signer():
    with pytest.raises(
        ValueError, match="Arguments signer and key_pair are mutually exclusive"
    ):
        Account(
            address=0x1,
            client=GatewayClient(net=TESTNET),
            chain=StarknetChainId.TESTNET,
            key_pair=KeyPair.from_private_key(0x111),
            signer=StarkCurveSigner(
                account_address=0x1,
                key_pair=KeyPair.from_private_key(0x11),
                chain_id=StarknetChainId.TESTNET,
            ),
        )
