import asyncio
import os.path
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.account.account_client import deploy_account_contract
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import parse_address, StarknetChainId
from starknet_py.net.networks import TESTNET, MAINNET
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")
erc20_mock_source_code = Path(directory, "erc20_mock.cairo").read_text("utf-8")

MAX_FEE = int(1e20)


@pytest.mark.asyncio
async def test_deploy_account_contract_and_sign_tx(run_devnet):
    acc_client = DevnetClientFactory(run_devnet).make_devnet_client()

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    map_contract = deployment_result.deployed_contract

    k, v = 13, 4324
    await (
        await map_contract.functions["put"].invoke(k, v, max_fee=MAX_FEE)
    ).wait_for_acceptance()
    (resp,) = await map_contract.functions["get"].call(k)

    assert resp == v


@pytest.mark.asyncio
async def test_get_balance_throws_when_token_not_specified(run_devnet):
    acc_client = DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(ValueError) as err:
        await acc_client.get_balance()

    assert "Token_address must be specified when using a custom net address" in str(
        err.value
    )


@pytest.mark.asyncio
async def test_balance_when_token_specified(run_devnet):
    acc_client = DevnetClientFactory(run_devnet).make_devnet_client()

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
    client = GatewayClient(net=net)
    acc_client = AccountClient(
        client=client, address="0x123", key_pair=KeyPair(123, 456)
    )

    with patch(
        "starknet_py.net.account.account_client.AccountClient.call_contract",
        MagicMock(),
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
    acc_client = DevnetClientFactory(run_devnet).make_devnet_client()

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
    acc_client = DevnetClientFactory(run_devnet).make_devnet_client()

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

    assert estimated_fee.overall_fee > 0


async def test_create_account_client(run_devnet):
    client = GatewayClient(net=run_devnet, chain=StarknetChainId.TESTNET)
    acc_client = await AccountClient.create_account(client)
    assert acc_client.signer is not None
    assert acc_client.address is not None


@pytest.mark.asyncio
async def test_create_account_client_with_private_key(run_devnet):
    private_key = 1234
    gt_client = GatewayClient(net=run_devnet, chain=StarknetChainId.TESTNET)
    acc_client = await AccountClient.create_account(
        client=gt_client, private_key=private_key
    )
    assert acc_client.signer.private_key == private_key
    assert acc_client.signer is not None
    assert acc_client.address is not None


@pytest.mark.asyncio
async def test_create_account_client_with_signer(run_devnet):
    key_pair = KeyPair.from_private_key(1234)
    client = GatewayClient(
        net=run_devnet,
        chain=StarknetChainId.TESTNET,
    )
    address = await deploy_account_contract(
        client=client,
        public_key=key_pair.public_key,
    )

    signer = StarkCurveSigner(
        account_address=address, key_pair=key_pair, chain_id=StarknetChainId.TESTNET
    )
    acc_client = await AccountClient.create_account(client=client, signer=signer)
    assert acc_client.signer == signer
    assert acc_client.signer is not None
    assert acc_client.address is not None


@pytest.mark.asyncio
async def test_sending_multicall(run_devnet):
    acc_client = DevnetClientFactory(run_devnet).make_devnet_client()

    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    calls = [
        contract.functions["put"].prepare(key=10, value=10),
        contract.functions["put"].prepare(key=20, value=20),
    ]

    res = await acc_client.execute(calls, int(1e20))
    await acc_client.wait_for_tx(res.hash)

    (value,) = await contract.functions["get"].call(key=20)

    assert res.code == "TRANSACTION_RECEIVED"
    assert value == 20

    @pytest.mark.asyncio
    async def test_get_block_traces(run_devnet):
        client = DevnetClientFactory(run_devnet).make_devnet_client()

        traces = await client.get_block_traces(block_number=0)

        assert traces.traces != []
