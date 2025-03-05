from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId, parse_address
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.tests.e2e.fixtures.constants import (
    MAX_RESOURCE_BOUNDS,
    STRK_FEE_CONTRACT_ADDRESS,
)


@pytest.mark.asyncio
async def test_get_balance_default_token_address():
    client = FullNodeClient(node_url="/rpc")
    acc_client = Account(
        client=client,
        address="0x123",
        key_pair=KeyPair(123, 456),
        chain=StarknetChainId.SEPOLIA,
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
async def test_account_get_balance_strk(account, hello_starknet_contract):
    balance = await account.get_balance(token_address=STRK_FEE_CONTRACT_ADDRESS)
    block = await account.client.get_block(block_number="latest")

    await hello_starknet_contract.functions["increase_balance"].invoke_v3(
        amount=10, resource_bounds=MAX_RESOURCE_BOUNDS
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
        chain=StarknetChainId.SEPOLIA,
    )

    assert account.address == 0x1
    assert account.signer.public_key == key_pair.public_key


@pytest.mark.parametrize(
    "chain",
    [
        StarknetChainId.SEPOLIA,
        "SN_SEPOLIA",
        "0x534e5f5345504f4c4941",
        393402133025997798000961,
    ],
)
def test_create_account_parses_chain(chain):
    key_pair = KeyPair.from_private_key(0x111)
    account = Account(
        address=0x1,
        client=FullNodeClient(node_url=""),
        key_pair=key_pair,
        chain=chain,
    )

    assert account.address == 0x1
    assert account.signer.public_key == key_pair.public_key
    assert isinstance(account.signer, StarkCurveSigner)
    assert account.signer.chain_id == 0x534E5F5345504F4C4941


def test_create_account_from_signer(client):
    signer = StarkCurveSigner(
        account_address=0x1,
        key_pair=KeyPair.from_private_key(0x111),
        chain_id=StarknetChainId.SEPOLIA,
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
            chain=StarknetChainId.SEPOLIA,
        )


def test_create_account_raises_on_both_keypair_and_signer():
    with pytest.raises(
        ValueError, match="Arguments signer and key_pair are mutually exclusive"
    ):
        Account(
            address=0x1,
            client=FullNodeClient(node_url=""),
            chain=StarknetChainId.SEPOLIA,
            key_pair=KeyPair.from_private_key(0x111),
            signer=StarkCurveSigner(
                account_address=0x1,
                key_pair=KeyPair.from_private_key(0x11),
                chain_id=StarknetChainId.SEPOLIA,
            ),
        )
