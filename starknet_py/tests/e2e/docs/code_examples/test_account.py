# pylint: disable=unused-variable
from unittest.mock import patch

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call, ResourceBounds, ResourceBoundsMapping
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.typed_data import TypedDataDict
from starknet_py.net.signer.key_pair import KeyPair


def test_init():
    # docs-start: init
    account = Account(
        address=0x123,
        client=FullNodeClient(node_url="https://your.node.url"),
        key_pair=KeyPair(12, 34),
        chain=StarknetChainId.SEPOLIA,
    )
    # docs-end: init


@pytest.mark.asyncio
async def test_execute_v3(account, contract_address):
    # docs-start: execute_v3
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
        l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    )
    resp = await account.execute_v3(
        Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[123],
        ),
        resource_bounds=resource_bounds,
    )
    # or
    # docs-end: execute_v3
    call1 = call2 = Call(
        to_addr=contract_address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[123],
    )
    # docs-start: execute_v3
    resp = await account.execute_v3(calls=[call1, call2], auto_estimate=True)
    # docs-end: execute_v3


@pytest.mark.asyncio
@patch(
    "starknet_py.net.account.account.Account.get_balance",
)
async def test_get_balance(account):
    # docs-start: get_balance
    eth_balance = await account.get_balance()
    # or with custom token contract address
    token_address = 0x1 or 1 or "0x1"
    # docs-end: get_balance
    token_address = FEE_CONTRACT_ADDRESS
    # docs-start: get_balance
    balance = await account.get_balance(token_address)
    # docs-end: get_balance


def test_sign_message(account):
    # docs-start: sign_message
    signature = account.sign_message(
        typed_data=TypedDataDict(
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
            domain={"name": "StarkNet Example", "version": "1", "chainId": "1"},
            message={"value": 1},
        )
    )
    # docs-end: sign_message


def test_verify_message(account):
    # docs-start: verify_message
    is_correct = account.verify_message(
        typed_data=TypedDataDict(
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
            domain={"name": "StarkNet Example", "version": "1", "chainId": "1"},
            message={"value": 1},
        ),
        signature=[12, 34],
    )
    # docs-end: verify_message
