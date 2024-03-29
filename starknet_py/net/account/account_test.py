from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId, parse_address
from starknet_py.net.networks import MAINNET
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner
from starknet_py.tests.e2e.fixtures.constants import (
    MAX_FEE,
    MAX_RESOURCE_BOUNDS_L1,
    STRK_FEE_CONTRACT_ADDRESS,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("net", (MAINNET))
async def test_get_balance_default_token_address(net):
    client = FullNodeClient(node_url=net + "/rpc")
    acc_client = Account(
        client=client,
        address="0x123",
        key_pair=KeyPair(123, 456),
        chain=StarknetChainId.MAINNET,
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
async def test_account_get_balance_eth(account, map_contract):
    balance = await account.get_balance()
    block = await account.client.get_block(block_number="latest")

    await map_contract.functions["put"].invoke_v1(key=10, value=10, max_fee=MAX_FEE)

    new_balance = await account.get_balance()
    old_balance = await account.get_balance(block_number=block.block_number)

    assert balance > 0
    assert new_balance < balance
    assert old_balance == balance


@pytest.mark.asyncio
async def test_account_get_balance_strk(account, map_contract):
    balance = await account.get_balance(token_address=STRK_FEE_CONTRACT_ADDRESS)
    block = await account.client.get_block(block_number="latest")

    await map_contract.functions["put"].invoke_v3(
        key=10, value=10, l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1
    )

    new_balance = await account.get_balance(token_address=STRK_FEE_CONTRACT_ADDRESS)
    old_balance = await account.get_balance(
        token_address=STRK_FEE_CONTRACT_ADDRESS, block_number=block.block_number
    )

    assert balance > 0
    assert new_balance < balance
    assert old_balance == balance


def test_create_account():
    key_pair = KeyPair.from_private_key(0x111)
    account = Account(
        address=0x1,
        client=FullNodeClient(node_url=""),
        key_pair=key_pair,
        chain=StarknetChainId.MAINNET,
    )

    assert account.address == 0x1
    assert account.signer.public_key == key_pair.public_key


def test_create_account_with_default_chain(client):
    key_pair = KeyPair.from_private_key(0x111)
    account = Account(
        address=0x2,
        client=client,
        key_pair=key_pair,
    )

    assert account.address == 0x2
    assert account.signer.public_key == key_pair.public_key
    assert isinstance(account.signer, StarkCurveSigner)
    assert account.signer.chain_id == StarknetChainId.MAINNET


def test_create_account_with_string_chain():
    key_pair = KeyPair.from_private_key(0x111)
    account = Account(
        address=0x2,
        client=FullNodeClient(node_url=""),
        key_pair=key_pair,
        chain="SN_SEPOLIA",
    )

    assert account.address == 0x2
    assert account.signer.public_key == key_pair.public_key
    assert isinstance(account.signer, StarkCurveSigner)
    assert account.signer.chain_id == 393402133025997798000961


def test_create_account_with_string_hex_chain():
    key_pair = KeyPair.from_private_key(0x111)
    account = Account(
        address=0x2,
        client=FullNodeClient(node_url=""),
        key_pair=key_pair,
        chain="0x534e5f5345504f4c4941",
    )

    assert account.address == 0x2
    assert account.signer.public_key == key_pair.public_key
    assert isinstance(account.signer, StarkCurveSigner)
    assert account.signer.chain_id == 393402133025997798000961


def test_create_account_from_signer(client):
    signer = StarkCurveSigner(
        account_address=0x1,
        key_pair=KeyPair.from_private_key(0x111),
        chain_id=StarknetChainId.MAINNET,
    )
    account = Account(address=0x1, client=client, signer=signer)

    assert account.address == 0x1
    assert account.signer == signer


def test_create_account_raises_on_no_keypair_and_signer():
    with pytest.raises(
        ValueError,
        match="Either a signer or a key_pair must be provided in Account constructor",
    ):
        Account(
            address=0x1,
            client=FullNodeClient(node_url=""),
            chain=StarknetChainId.MAINNET,
        )


def test_create_account_raises_on_both_keypair_and_signer():
    with pytest.raises(
        ValueError, match="Arguments signer and key_pair are mutually exclusive"
    ):
        Account(
            address=0x1,
            client=FullNodeClient(node_url=""),
            chain=StarknetChainId.MAINNET,
            key_pair=KeyPair.from_private_key(0x111),
            signer=StarkCurveSigner(
                account_address=0x1,
                key_pair=KeyPair.from_private_key(0x11),
                chain_id=StarknetChainId.MAINNET,
            ),
        )
