import pytest

from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner


@pytest.mark.asyncio
async def test_creating_account_client(network):
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net import AccountClient, KeyPair
    from starknet_py.net.models.chains import StarknetChainId
    from starknet_py.net.gateway_client import GatewayClient

    testnet = "testnet"
    chain_id = StarknetChainId.TESTNET
    # add to docs: end
    testnet = network
    # add to docs: start

    # Creates an instance of account client which is already deployed (testnet)

    # old AccountClient using transaction version=0 (doesn't have __validate__ function)
    client = GatewayClient(net=testnet)
    account_client_testnet = AccountClient(
        client=client,
        address="0x1234",
        key_pair=KeyPair(private_key=123, public_key=456),
        chain=StarknetChainId.TESTNET,
        supported_tx_version=0,
    )

    # new AccountClient using transaction version=1 (does have __validate__ function)
    client = GatewayClient(net=testnet)
    account_client_testnet = AccountClient(
        client=client,
        address="0x4321",
        key_pair=KeyPair(private_key=654, public_key=321),
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )

    # There is another way of creating key_pair
    key_pair = KeyPair.from_private_key(key=123)

    # Instead of providing key_pair it is possible to specify a signer
    signer = StarkCurveSigner("0x1234", key_pair, StarknetChainId.TESTNET)

    account_client = AccountClient(client=client, address="0x1234", signer=signer)

    # Deploys an account on testnet and returns an instance
    account_client = await AccountClient.create_account(
        client=client, chain=StarknetChainId.TESTNET
    )
    # add to docs: end
