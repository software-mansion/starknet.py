from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId, parse_address
from starknet_py.net.networks import MAINNET, TESTNET
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


@pytest.mark.asyncio
@pytest.mark.parametrize("net", (TESTNET, MAINNET))
async def test_get_balance_default_token_address(net):
    client = FullNodeClient(node_url=net + "/rpc")
    acc_client = Account(
        client=client,
        address="0x123",
        key_pair=KeyPair(123, 456),
        chain=StarknetChainId.TESTNET,
    )

    with patch(
        f"{FullNodeClient.__module__}.FullNodeClient.call_contract",
        AsyncMock(),
    ) as mocked_call_contract:
        mocked_call_contract.return_value = [0, 0]

        await acc_client.get_balance()

        call = mocked_call_contract.call_args

    (call,) = call[0]

    assert call.to_addr == parse_address(FEE_CONTRACT_ADDRESS)


@pytest.mark.asyncio
async def test_account_get_balance(account, map_contract):
    balance = await account.get_balance()
    block = await account.client.get_block(block_number="latest")

    await map_contract.functions["put"].invoke(
        key=10, value=10, tx_version=1, max_fee=MAX_FEE
    )

    new_balance = await account.get_balance()
    old_balance = await account.get_balance(block_number=block.block_number)

    assert balance > 0
    assert new_balance < balance
    assert old_balance == balance


def test_create_account():
    key_pair = KeyPair.from_private_key(0x111)
    account = Account(
        address=0x1,
        client=FullNodeClient(node_url=""),
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
    account = Account(address=0x1, client=FullNodeClient(node_url=""), signer=signer)

    assert account.address == 0x1
    assert account.signer == signer


def test_create_account_raises_on_no_chain_and_signer():
    with pytest.raises(ValueError, match="One of chain or signer must be provided"):
        Account(
            address=0x1,
            client=FullNodeClient(node_url=""),
            key_pair=KeyPair.from_private_key(0x111),
        )


def test_create_account_raises_on_no_keypair_and_signer():
    with pytest.raises(
        ValueError,
        match="Either a signer or a key_pair must be provided in Account constructor",
    ):
        Account(
            address=0x1,
            client=FullNodeClient(node_url=""),
            chain=StarknetChainId.TESTNET,
        )


def test_create_account_raises_on_both_keypair_and_signer():
    with pytest.raises(
        ValueError, match="Arguments signer and key_pair are mutually exclusive"
    ):
        Account(
            address=0x1,
            client=FullNodeClient(node_url=""),
            chain=StarknetChainId.TESTNET,
            key_pair=KeyPair.from_private_key(0x111),
            signer=StarkCurveSigner(
                account_address=0x1,
                key_pair=KeyPair.from_private_key(0x11),
                chain_id=StarknetChainId.TESTNET,
            ),
        )
