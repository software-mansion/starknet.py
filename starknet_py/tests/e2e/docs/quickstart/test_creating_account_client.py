import pytest

from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner


@pytest.mark.asyncio
async def test_creating_account_client(run_devnet):
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net import AccountClient, KeyPair
    from starknet_py.net.models.chains import StarknetChainId
    from starknet_py.net.gateway_client import GatewayClient

    testnet = "testnet"
    chain_id = StarknetChainId.TESTNET
    # add to docs: end
    testnet = run_devnet
    # add to docs: start

    # Creates an instance of account client which is already deployed (testnet):
    client = GatewayClient(net=testnet)
    account_client_testnet = AccountClient(
        client=client,
        address="0x1234",
        key_pair=KeyPair(private_key=123, public_key=456),
        chain=StarknetChainId.TESTNET,
    )

    # There is another way of creating key_pair
    key_pair = KeyPair.from_private_key(key=123)

    # Instead of providing key_pair it is possible to specify a signer
    signer = StarkCurveSigner("0x1234", key_pair, StarknetChainId.TESTNET)

    account_client = AccountClient(client=client, address="0x1234", signer=signer)

    # Deploys an account on testnet and returns an instance
    account_client = await AccountClient.create_account(client=client)
    # add to docs: end
