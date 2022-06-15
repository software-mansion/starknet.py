import asyncio
import os.path
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.account.account_client import deploy_account_contract
from starknet_py.net.models import InvokeFunction, parse_address, StarknetChainId
from starknet_py.net.networks import TESTNET, MAINNET
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")
erc20_mock_source_code = Path(directory, "erc20_mock.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_declare(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

    res = await acc_client.declare(compilation_source=erc20_mock_source_code)

    assert res["class_hash"] is not None


@pytest.mark.asyncio
async def test_declare_raises_when_missing_source(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(ValueError) as v_err:
        await acc_client.declare()

    assert "One of compiled_contract or compilation_source is required." in str(
        v_err.value
    )


@pytest.mark.asyncio
async def test_deploy_account_contract_and_sign_tx(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

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
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

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
async def test_get_balance_throws_when_token_not_specified(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(ValueError) as err:
        await acc_client.get_balance()

    assert "Token_address must be specified when using a custom net address" in str(
        err.value
    )


@pytest.mark.asyncio
async def test_balance_when_token_specified(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=erc20_mock_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    erc20_contract = deployment_result.deployed_contract

    balance = await acc_client.get_balance(erc20_contract.address)

    assert balance == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("net", (TESTNET, MAINNET))
async def test_get_balance_default_token_address(net):
    acc_client = AccountClient("0x123", key_pair=KeyPair(123, 456), net=net)

    with patch(
        "starknet_py.net.client.Client.call_contract", MagicMock()
    ) as mocked_call_contract:
        result = asyncio.Future()
        result.set_result([0, 0])

        mocked_call_contract.return_value = result

        await acc_client.get_balance()

        call = mocked_call_contract.call_args

    (invoke_tx,) = call[0]

    assert invoke_tx.contract_address == parse_address(FEE_CONTRACT_ADDRESS)


@pytest.mark.asyncio
async def test_estimate_fee_called(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=erc20_mock_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    erc20_contract = deployment_result.deployed_contract

    with patch(
        "starknet_py.net.account.account_client.AccountClient.estimate_fee", MagicMock()
    ) as mocked_estimate_fee:
        result = asyncio.Future()
        result.set_result([0])

        mocked_estimate_fee.return_value = result

        await erc20_contract.functions["balanceOf"].prepare(
            "1234", max_fee=0
        ).estimate_fee()

        mocked_estimate_fee.assert_called()


@pytest.mark.asyncio
async def test_estimated_fee_greater_than_zero(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=erc20_mock_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    erc20_contract = deployment_result.deployed_contract

    estimated_fee = (
        await erc20_contract.functions["balanceOf"]
        .prepare("1234", max_fee=0)
        .estimate_fee()
    )

    assert estimated_fee > 0


@pytest.mark.asyncio
async def test_fee_higher_for_account_client(run_devnet):
    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()
    client = await DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=erc20_mock_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()

    contract_acc = deployment_result.deployed_contract
    contract_client = await Contract.from_address(contract_acc.address, client)

    estimated_fee_signed = (
        await contract_acc.functions["balanceOf"]
        .prepare("1234", max_fee=0)
        .estimate_fee()
    )

    estimated_fee = (
        await contract_client.functions["balanceOf"]
        .prepare("1234", max_fee=0)
        .estimate_fee()
    )

    assert estimated_fee < estimated_fee_signed


@pytest.mark.asyncio
async def test_create_account_client(run_devnet):
    acc_client = await AccountClient.create_account(
        net=run_devnet, chain=StarknetChainId.TESTNET
    )
    assert acc_client.signer is not None
    assert acc_client.address is not None


@pytest.mark.asyncio
async def test_create_account_client_with_private_key(run_devnet):
    private_key = 1234
    acc_client = await AccountClient.create_account(
        net=run_devnet, chain=StarknetChainId.TESTNET, private_key=private_key
    )
    assert acc_client.signer.private_key == private_key
    assert acc_client.signer is not None
    assert acc_client.address is not None


@pytest.mark.asyncio
async def test_create_account_client_with_signer(run_devnet):
    key_pair = KeyPair.from_private_key(1234)
    address = await deploy_account_contract(
        public_key=key_pair.public_key, net=run_devnet, chain=StarknetChainId.TESTNET
    )

    signer = StarkCurveSigner(
        account_address=address, key_pair=key_pair, chain_id=StarknetChainId.TESTNET
    )
    acc_client = await AccountClient.create_account(
        net=run_devnet, chain=StarknetChainId.TESTNET, signer=signer
    )
    assert acc_client.signer == signer
    assert acc_client.signer is not None
    assert acc_client.address is not None
