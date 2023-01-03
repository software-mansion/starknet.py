import pytest

from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner


@pytest.mark.asyncio
async def test_creating_account(network):
    # pylint: disable=import-outside-toplevel, unused-variable
    # docs: start
    from starknet_py.net import AccountClient, KeyPair
    from starknet_py.net.account.account import Account
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.models.chains import StarknetChainId

    testnet = "testnet"
    chain_id = StarknetChainId.TESTNET
    # docs: end
    testnet = network
    # docs: start

    # Creates an instance of account client which is already deployed (testnet)

    # old AccountClient using transaction version=0 (doesn't have __validate__ function)
    # Warning: AccountClient is deprecated! Unless you need to use transactions with version=0,
    # please migrate to using new Account.
    client = GatewayClient(net=testnet)
    account_client_testnet = AccountClient(
        client=client,
        address="0x1234",
        key_pair=KeyPair(private_key=123, public_key=456),
        chain=StarknetChainId.TESTNET,
        supported_tx_version=0,
    )

    # new Account using transaction version=1 (has __validate__ function)
    # It is not compatible with version=0. To use an old account contract, AccountClient must be used.
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
