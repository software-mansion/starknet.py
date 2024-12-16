import pytest

from starknet_py.net.signer.key_pair import KeyPair


@pytest.mark.asyncio
async def test_creating_account():
    # pylint: disable=import-outside-toplevel, unused-variable
    # docs: start
    from starknet_py.net.account.account import Account
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.models.chains import StarknetChainId
    from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

    # Creates an instance of account which is already deployed
    # Account using transaction version=1 (has __validate__ function)
    client = FullNodeClient(node_url="https://your.node.url")
    account = Account(
        client=client,
        address="0x4321",
        key_pair=KeyPair(private_key=654, public_key=321),
        chain=StarknetChainId.SEPOLIA,
    )

    # There is another way of creating key_pair
    key_pair = KeyPair.from_private_key(key=123)
    # or
    key_pair = KeyPair.from_private_key(key="0x123")

    # Instead of providing key_pair it is possible to specify a signer
    signer = StarkCurveSigner("0x1234", key_pair, StarknetChainId.SEPOLIA)

    account = Account(
        client=client, address="0x1234", signer=signer, chain=StarknetChainId.SEPOLIA
    )
    # docs: end
