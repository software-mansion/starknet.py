import pytest_asyncio

from starknet_py.net import AccountClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.tests.e2e.conftest import MAX_FEE


@pytest_asyncio.fixture
async def deploy_account_transaction(
    details_of_account_to_be_deployed, network: str
) -> DeployAccount:
    """
    Returns a DeployAccount transaction
    """
    address, key_pair, salt, class_hash = details_of_account_to_be_deployed

    account = AccountClient(
        address=address,
        client=GatewayClient(net=network),
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )
    return await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        max_fee=MAX_FEE,
    )
