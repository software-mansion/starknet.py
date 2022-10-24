import pytest
from starkware.starknet.public.abi import get_storage_var_address

from starknet_py.net.client_models import (
    TransactionStatusResponse,
    TransactionStatus,
    DeployedContract,
    DeployAccountTransaction,
)
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.networks import TESTNET, MAINNET, CustomGatewayUrls


@pytest.mark.asyncio
async def test_gateway_raises_on_both_block_hash_and_number(
    block_with_deploy_number, gateway_client
):
    with pytest.raises(ValueError) as exinfo:
        await gateway_client.get_block(
            block_hash="0x0", block_number=block_with_deploy_number
        )

    assert "block_hash and block_number parameters are mutually exclusive" in str(
        exinfo.value
    )


@pytest.mark.asyncio
async def test_get_class_hash_at(contract_address, gateway_client, class_hash):
    class_hash_resp = await gateway_client.get_class_hash_at(
        contract_address=contract_address
    )

    assert class_hash_resp == class_hash


@pytest.mark.asyncio
async def test_get_code(contract_address, gateway_client):
    code = await gateway_client.get_code(contract_address=contract_address)

    assert code.abi is not None
    assert len(code.abi) != 0
    assert code.bytecode is not None
    assert len(code.bytecode) != 0


@pytest.mark.asyncio
async def test_get_contract_nonce(gateway_client):
    nonce = await gateway_client.get_contract_nonce(
        contract_address=0x1111,
        block_hash="latest",
    )
    assert nonce == 0


@pytest.mark.asyncio
async def test_get_transaction_status(invoke_transaction_hash, gateway_client):
    tx_status_resp = await gateway_client.get_transaction_status(
        invoke_transaction_hash
    )
    assert isinstance(tx_status_resp, TransactionStatusResponse)
    assert tx_status_resp.transaction_status == TransactionStatus.ACCEPTED_ON_L2
    assert isinstance(tx_status_resp.block_hash, int)


# pylint: disable=protected-access
@pytest.mark.parametrize(
    "net, net_address",
    (
        (TESTNET, "https://alpha4.starknet.io"),
        (MAINNET, "https://alpha-mainnet.starknet.io"),
    ),
)
def test_creating_client_from_predefined_network(net, net_address):
    gateway_client = GatewayClient(net=net)

    assert gateway_client.net == net
    assert gateway_client._feeder_gateway_client.url == f"{net_address}/feeder_gateway"
    assert gateway_client._gateway_client.url == f"{net_address}/gateway"


def test_creating_client_with_custom_net():
    custom_net = "custom.net"
    gateway_client = GatewayClient(net=custom_net)

    assert gateway_client.net == custom_net
    assert gateway_client._feeder_gateway_client.url == f"{custom_net}/feeder_gateway"
    assert gateway_client._gateway_client.url == f"{custom_net}/gateway"


def test_creating_client_with_custom_net_dict():
    custom_net = "custom.net"
    net = CustomGatewayUrls(
        feeder_gateway_url=f"{custom_net}/feeder_gateway",
        gateway_url=f"{custom_net}/gateway",
    )

    gateway_client = GatewayClient(net=net)

    assert gateway_client.net == net
    assert gateway_client._feeder_gateway_client.url == net["feeder_gateway_url"]
    assert gateway_client._gateway_client.url == net["gateway_url"]


@pytest.mark.asyncio
async def test_estimate_fee_deploy_account(gateway_client, deploy_account_transaction):
    estimate_fee = await gateway_client.estimate_fee(tx=deploy_account_transaction)

    assert isinstance(estimate_fee.overall_fee, int)
    assert estimate_fee.overall_fee > 0


@pytest.mark.asyncio
async def test_state_update_gateway_client(
    gateway_client,
    block_with_deploy_number,
    contract_address,
    class_hash,
):
    state_update = await gateway_client.get_state_update(
        block_number=block_with_deploy_number
    )

    assert (
        DeployedContract(
            address=contract_address,
            class_hash=class_hash,
        )
        in state_update.deployed_contracts
    )


@pytest.mark.asyncio
async def test_get_storage_at_incorrect_address_gateway_client(gateway_client):
    storage = await gateway_client.get_storage_at(
        contract_address=0x1111,
        key=get_storage_var_address("balance"),
        block_hash="latest",
    )
    assert storage == 0


@pytest.mark.asyncio
async def test_get_deploy_account_transaction(
    gateway_client, deploy_account_transaction_hash
):
    # TODO Modify this test to also use FullNodeClient (move to client_test)
    transaction = await gateway_client.get_transaction(deploy_account_transaction_hash)

    assert isinstance(transaction, DeployAccountTransaction)
    assert transaction.hash == deploy_account_transaction_hash
    assert len(transaction.signature) > 0
    assert transaction.nonce == 0
