# pylint: disable=unused-variable
from unittest.mock import patch

import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.typed_data import TypedData
from starknet_py.net.networks import TESTNET
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner


def test_init():
    # docs-start: init
    account = Account(
        address=0x123,
        client=GatewayClient(net=TESTNET),
        signer=StarkCurveSigner(
            account_address=0x123,
            key_pair=KeyPair(12, 34),
            chain_id=StarknetChainId.TESTNET,
        ),
    )
    # or
    account = Account(
        address=0x123,
        client=FullNodeClient(node_url="your.node.url", net="testnet"),
        key_pair=KeyPair(12, 34),
        chain=StarknetChainId.TESTNET,
    )
    # docs-end: init


@pytest.mark.asyncio
async def test_execute(gateway_account, contract_address):
    account = gateway_account
    # docs-start: execute
    resp = await account.execute(
        Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[123],
        ),
        max_fee=int(1e15),
    )
    # or
    # docs-end: execute
    call1 = call2 = Call(
        to_addr=contract_address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[123],
    )
    # docs-start: execute
    resp = await account.execute(calls=[call1, call2], auto_estimate=True)
    # docs-end: execute


@pytest.mark.asyncio
@patch(
    "starknet_py.net.account.account.Account.get_balance",
)
async def test_get_balance(gateway_account):
    account = gateway_account
    # docs-start: get_balance
    eth_balance = await account.get_balance()
    # or with custom token contract address
    token_address = 0x1 or 1 or "0x1"
    # docs-end: get_balance
    token_address = FEE_CONTRACT_ADDRESS
    # docs-start: get_balance
    balance = await account.get_balance(token_address)
    # docs-end: get_balance


def test_sign_message(gateway_account):
    account = gateway_account
    # docs-start: sign_message
    signature = account.sign_message(
        typed_data=TypedData(
            types={
                "StarkNetDomain": [
                    {"name": "name", "type": "felt"},
                    {"name": "version", "type": "felt"},
                    {"name": "chainId", "type": "felt"},
                ],
                "Example": [
                    {"name": "value", "type": "felt"},
                ],
            },
            primaryType="Example",
            domain={"name": "StarkNet Example", "version": "1", "chainId": 1},
            message={"value": 1},
        )
    )
    # docs-end: sign_message


def test_verify_message(gateway_account):
    account = gateway_account
    # docs-start: verify_message
    is_correct = account.verify_message(
        typed_data=TypedData(
            types={
                "StarkNetDomain": [
                    {"name": "name", "type": "felt"},
                    {"name": "version", "type": "felt"},
                    {"name": "chainId", "type": "felt"},
                ],
                "Example": [
                    {"name": "value", "type": "felt"},
                ],
            },
            primaryType="Example",
            domain={"name": "StarkNet Example", "version": "1", "chainId": 1},
            message={"value": 1},
        ),
        signature=[12, 34],
    )
    # docs-end: verify_message
