import pytest

from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner


@pytest.mark.asyncio
async def test_creating_account_client(run_devnet):
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net import AccountClient, KeyPair
    from starknet_py.net.models import StarknetChainId
    from starknet_py.net.networks import TESTNET, MAINNET

    # Creates an instance of account client which is already deployed
    # mainnet
    account_client_mainnet = AccountClient(
        address="0x1234",
        key_pair=KeyPair(private_key=123, public_key=456),
        net=MAINNET,
    )

    # testnet
    account_client_testnet = AccountClient(
        address="0x1234",
        key_pair=KeyPair(private_key=123, public_key=456),
        net=TESTNET,
    )

    # There is another way of creating key_pair
    key_pair = KeyPair.from_private_key(key=123)

    # Instead of providing key_pair it is possible to specify a signer
    signer = StarkCurveSigner("0x1234", key_pair, StarknetChainId.TESTNET)

    account_client = AccountClient(address="0x1234", signer=signer, net=TESTNET)

    testnet = "testnet"
    # add to docs: end
    testnet = run_devnet
    # add to docs: start

    # Deploys an account on testnet and returns an instance
    account_client = await AccountClient.create_account(
        net=testnet, chain=StarknetChainId.TESTNET
    )
    # add to docs: end
