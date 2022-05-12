import os.path
from pathlib import Path
from typing import Optional, List
from unittest.mock import patch

import pytest
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    CastableToHash,
    BlockIdentifier,
)

from starknet_py.constants import TESTNET_ETH_CONTRACT, MAINNET_ETH_CONTRACT
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.client import BadRequest, Client
from starknet_py.net.models import StarknetChainId, InvokeFunction, parse_address
from starknet_py.net.networks import TESTNET, MAINNET

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")
erc20_mock_source_code = Path(directory, "erc20_mock.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_deploy_account_contract_and_sign_tx(run_devnet):
    acc_client = await AccountClient.create_account(
        net=run_devnet, chain=StarknetChainId.TESTNET
    )

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    map_contract = deployment_result.deployed_contract

    k, v = 13, 4324
    await (
        await map_contract.functions["put"].invoke(k, v, max_fee=0)
    ).wait_for_acceptance()
    (resp,) = await map_contract.functions["get"].call(k)

    assert resp == v


@pytest.mark.asyncio
async def test_error_when_tx_signed(run_devnet):
    acc_client = await AccountClient.create_account(
        net=run_devnet, chain=StarknetChainId.TESTNET
    )

    invoke_function = InvokeFunction(
        contract_address=123,
        entry_point_selector=123,
        calldata=[],
        signature=[123, 321],
        max_fee=10,
        version=0,
    )
    with pytest.raises(TypeError) as t_err:
        await acc_client.add_transaction(tx=invoke_function)

    assert "Adding signatures to a signer tx currently isn't supported" in str(
        t_err.value
    )


@pytest.mark.asyncio
async def test_error_when_token_not_specified(run_devnet):
    acc_client = await AccountClient.create_account(
        net=run_devnet, chain=StarknetChainId.TESTNET
    )

    with pytest.raises(BadRequest) as b_req:
        await acc_client.get_balance()

    assert "Specify token_address for custom url." in str(b_req.value)


@pytest.mark.asyncio
async def test_balance_when_token_specified(run_devnet):
    acc_client = await AccountClient.create_account(
        net=run_devnet, chain=StarknetChainId.TESTNET
    )

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=erc20_mock_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    erc20_contract = deployment_result.deployed_contract

    balance = await acc_client.get_balance(erc20_contract.address)

    assert balance == 200


async def mocked_call_contract(
    self,
    invoke_tx: InvokeFunction,
    block_hash: Optional[CastableToHash] = None,
    block_number: Optional[BlockIdentifier] = None,
) -> List[int]:
    return [0]


@patch.object(Client, "call_contract", mocked_call_contract)
@pytest.mark.asyncio
async def test_default_token_address(run_devnet):
    acc_client_testnet = AccountClient("0x123", KeyPair(123, 456), TESTNET)
    acc_client_mainnet = AccountClient("0x321", KeyPair(456, 123), MAINNET)


