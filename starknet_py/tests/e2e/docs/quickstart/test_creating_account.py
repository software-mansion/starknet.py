import pytest

from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner


@pytest.mark.asyncio
async def test_creating_account(network):
    # pylint: disable=import-outside-toplevel, unused-variable
    # docs: start
    from starknet_py.net.account.account import Account
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.models.chains import StarknetChainId
    from starknet_py.net.signer.stark_curve_signer import KeyPair

    testnet = "testnet"
    # docs: end
    testnet = network
    # docs: start

    # Creates an instance of account which is already deployed (testnet)

    # Account using transaction version=1 (has __validate__ function)
    client = GatewayClient(net=testnet)
    account = Account(
        client=client,
        address="0x4321",
        key_pair=KeyPair(private_key=654, public_key=321),
        chain=StarknetChainId.TESTNET,
    )

    # There is another way of creating key_pair
    key_pair = KeyPair.from_private_key(key=123)

    # Instead of providing key_pair it is possible to specify a signer
    signer = StarkCurveSigner("0x1234", key_pair, StarknetChainId.TESTNET)

    account = Account(client=client, address="0x1234", signer=signer)
    # docs: end
