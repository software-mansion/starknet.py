import asyncio
import os.path
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from starknet_py.constants import TESTNET_ETH_CONTRACT, MAINNET_ETH_CONTRACT
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.client import BadRequest
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


@pytest.mark.asyncio
async def test_default_token_address():

    acc_client_testnet = AccountClient("0x123", KeyPair(123, 456), TESTNET)
    acc_client_mainnet = AccountClient("0x321", KeyPair(456, 123), MAINNET)

    with patch(
        "starknet_py.net.client.Client.call_contract", MagicMock()
    ) as mocked_call_contract:
        result = asyncio.Future()
        result.set_result([0])

        mocked_call_contract.return_value = result

        await acc_client_testnet.get_balance()
        await acc_client_mainnet.get_balance()

        calls = mocked_call_contract.call_args_list

    call_testnet, call_mainnet = calls[0], calls[1]

    (invoke_tx1,) = call_testnet[0]
    (invoke_tx2,) = call_mainnet[0]

    assert invoke_tx1.contract_address == parse_address(TESTNET_ETH_CONTRACT)
    assert invoke_tx2.contract_address == parse_address(MAINNET_ETH_CONTRACT)
