# pylint: disable=unused-variable
import pytest

from starknet_py.contract import Contract
from starknet_py.net import KeyPair
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import TESTNET


def test_init():
    # docs-start: init
    contract = Contract(
        address=0x123,
        abi=[
            {
                "inputs": [{"name": "amount", "type": "felt"}],
                "name": "increase_balance",
                "outputs": [],
                "type": "function",
            },
        ],
        provider=Account(
            address=0x321,
            client=GatewayClient(TESTNET),
            key_pair=KeyPair(12, 34),
            chain=StarknetChainId.TESTNET,
        ),
    )
    # docs-end: init


@pytest.mark.asyncio
async def test_from_address(gateway_account, contract_address):
    account = gateway_account
    # docs-start: from_address
    address = 1 or 0x1 or "0x1"
    # docs-end: from_address
    address = contract_address
    # docs-start: from_address
    contract = await Contract.from_address(address=address, provider=account)
    # or if the contract is a proxy (read more about resolving proxies in the `Guide`)
    config = True
    # docs-end: from_address
    config = False
    # docs-start: from_address
    contract = await Contract.from_address(
        address=address, provider=account, proxy_config=config
    )
    # docs-end: from_address


@pytest.mark.asyncio
async def test_declare(gateway_account, custom_proxy):
    account = gateway_account
    compiled_with_cli = custom_proxy
    # docs-start: declare
    declare_result = await Contract.declare(
        account=account, compiled_contract=compiled_with_cli, max_fee=int(1e15)
    )
    # docs-end: declare


@pytest.mark.asyncio
async def test_deploy_contract(gateway_account, class_hash):
    account = gateway_account
    # docs-start: deploy_contract
    deploy_result = await Contract.deploy_contract(
        account=account,
        class_hash=class_hash,
        abi=[
            {
                "inputs": [{"name": "amount", "type": "felt"}],
                "name": "increase_balance",
                "outputs": [],
                "type": "function",
            }
        ],
        max_fee=int(1e15),
    )
    # or when there is a constructor
    deploy_result = await Contract.deploy_contract(
        account=account,
        class_hash=class_hash,
        abi=[
            {
                "inputs": [{"name": "value", "type": "felt"}],
                "name": "constructor",
                "outputs": [],
                "type": "constructor",
            },
        ],
        constructor_args={"value": 1},
        max_fee=int(1e15),
    )
    # docs-end: deploy_contract


def test_compute_address(custom_proxy):
    compiled_with_cli = custom_proxy
    # docs-start: compute_address
    address = Contract.compute_address(
        salt=1, compiled_contract=compiled_with_cli, constructor_args=[1, 2, [2]]
    )
    # docs-end: compute_address
