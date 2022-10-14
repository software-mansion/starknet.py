from typing import Tuple

import pytest
import pytest_asyncio
from starkware.starknet.definitions.fields import ContractAddressSalt

from starknet_py.net import AccountClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.tests.e2e.client.prepare_net_for_gateway_test import (
    PreparedNetworkData,
)
from starknet_py.tests.e2e.conftest import MAX_FEE


@pytest_asyncio.fixture
async def deploy_account_transaction(
    details_of_account_to_be_deployed, network: str
) -> DeployAccount:
    """
    Returns a DeployAccount transaction
    """
    address, key_pair, _, class_hash = details_of_account_to_be_deployed

    account = AccountClient(
        address=address,
        client=GatewayClient(net=network),
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )
    return await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=ContractAddressSalt.get_random_value(),
        constructor_calldata=[key_pair.public_key],
        max_fee=MAX_FEE,
    )


@pytest.fixture
def deploy_account_transaction_hash(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns hash of deploy account transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.deploy_account_transaction_hash


@pytest.fixture
def block_with_deploy_account_number(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns number of the block with deploy account transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_deploy_account_number
