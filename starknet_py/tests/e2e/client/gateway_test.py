import pytest

from starknet_py.net.client_models import TransactionStatusResponse, TransactionStatus
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import TESTNET, MAINNET, net_address_from_net


@pytest.mark.asyncio
async def test_gateway_raises_on_both_block_hash_and_number(
    block_with_deploy_hash, gateway_client
):
    with pytest.raises(ValueError) as exinfo:
        await gateway_client.get_block(
            block_hash=block_with_deploy_hash, block_number=0
        )

    assert "block_hash and block_number parameters are mutually exclusive" in str(
        exinfo.value
    )


@pytest.mark.asyncio
async def test_get_class_hash_at(contract_address, gateway_client):
    class_hash = await gateway_client.get_class_hash_at(
        contract_address=contract_address
    )

    assert (
        class_hash
        == 3197248528421459336430560285234479619486870042069853528940753151314137720584
    )


@pytest.mark.asyncio
async def test_get_code(contract_address, gateway_client):
    code = await gateway_client.get_code(contract_address=contract_address)

    assert code.abi is not None
    assert len(code.abi) != 0
    assert code.bytecode is not None
    assert len(code.bytecode) != 0


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
    "net, chain",
    ((TESTNET, StarknetChainId.TESTNET), (MAINNET, StarknetChainId.MAINNET)),
)
def test_creating_client_from_predefined_network(net, chain):
    gateway_client = GatewayClient(net=net)
    net_address = net_address_from_net(net)

    assert gateway_client.net == net
    assert gateway_client._feeder_gateway_client.url == f"{net_address}/feeder_gateway"
    assert gateway_client._gateway_client.url == f"{net_address}/gateway"
    assert gateway_client.chain == chain


def test_creating_client_with_custom_net(run_devnet):
    gateway_client = GatewayClient(net=run_devnet, chain=StarknetChainId.TESTNET)

    assert gateway_client.net == run_devnet
    assert gateway_client._feeder_gateway_client.url == f"{run_devnet}/feeder_gateway"
    assert gateway_client._gateway_client.url == f"{run_devnet}/gateway"
    assert gateway_client.chain == StarknetChainId.TESTNET


def test_creating_client_with_custom_net_dict(run_devnet):
    net = {
        "feeder_gateway_url": f"{run_devnet}/feeder_gateway",
        "gateway_url": f"{run_devnet}/gateway",
    }

    gateway_client = GatewayClient(net=net, chain=StarknetChainId.TESTNET)

    assert gateway_client.net == net
    assert gateway_client._feeder_gateway_client.url == net["feeder_gateway_url"]
    assert gateway_client._gateway_client.url == net["gateway_url"]
    assert gateway_client.chain == StarknetChainId.TESTNET


def test_throwing_on_custom_net_dict_without_chain(run_devnet):
    net = {
        "feeder_gateway_url": f"{run_devnet}/feeder_gateway",
        "gateway_url": f"{run_devnet}/gateway",
    }

    with pytest.raises(ValueError) as err:
        GatewayClient(net=net)

    assert "Chain is required when not using predefined networks." == str(err.value)
