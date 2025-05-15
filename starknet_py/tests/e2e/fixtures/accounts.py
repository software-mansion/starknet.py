# pylint: disable=redefined-outer-name
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pytest
import pytest_asyncio

from starknet_py.constants import ARGENT_V040_CLASS_HASH
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client_models import PriceUnit
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.http_client import HttpMethod, RpcHttpClient
from starknet_py.net.models import AddressRepresentation, StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS,
    DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY,
    MAX_RESOURCE_BOUNDS,
)
from starknet_py.tests.e2e.utils import (
    AccountToBeDeployedDetails,
    _get_random_private_key_unsafe,
    _new_address,
    get_deploy_account_transaction,
    prepay_account,
)


@dataclass
class AccountPrerequisites:
    address: AddressRepresentation
    salt: int
    calldata: list[int]
    key_pair: KeyPair


async def devnet_account_details(
    client: FullNodeClient,
    class_hash: int,
    devnet,
) -> Tuple[str, str]:
    """
    Deploys an Account and adds fee tokens to its balance (only on devnet).
    """

    private_key = _get_random_private_key_unsafe()
    key_pair = KeyPair.from_private_key(private_key)
    salt = 1

    address = compute_address(
        class_hash=class_hash,
        constructor_calldata=[key_pair.public_key],
        salt=salt,
        deployer_address=0,
    )

    await mint_token_on_devnet(devnet, address, int(1e30), PriceUnit.WEI.value)
    await mint_token_on_devnet(devnet, address, int(1e30), PriceUnit.FRI.value)

    deploy_account_tx = await get_deploy_account_transaction(
        address=address,
        key_pair=key_pair,
        salt=salt,
        class_hash=class_hash,
        client=client,
    )

    account = Account(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA,
    )
    res = await account.client.deploy_account(deploy_account_tx)
    await account.client.wait_for_tx(res.transaction_hash)

    return hex(address), hex(key_pair.private_key)


async def mint_token_on_devnet(url: str, address: int, amount: int, unit: str):
    http_client = RpcHttpClient(url)
    await http_client.request(
        http_method=HttpMethod.POST,
        address=f"{url}/mint",
        payload={"address": hex(address), "amount": amount, "unit": unit},
    )


@pytest.fixture(name="account", scope="package")
def full_node_account(client: FullNodeClient) -> BaseAccount:
    """
    Returns a new Account created with FullNodeClient.
    """
    address = DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS
    private_key = DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY

    return Account(
        address=address,
        client=client,
        key_pair=KeyPair.from_private_key(int(private_key, 0)),
        chain=StarknetChainId.SEPOLIA,
    )


@dataclass
class AccountToBeDeployedDetailsFactory:
    class_hash: int
    eth_fee_contract: Contract
    strk_fee_contract: Contract

    async def get(
        self,
        *,
        class_hash: Optional[int] = None,
        calldata: Optional[List[int]] = None,
    ) -> AccountToBeDeployedDetails:
        key_pair = KeyPair.from_private_key(_get_random_private_key_unsafe())

        calldata = calldata if calldata is not None else []
        class_hash = class_hash if class_hash is not None else self.class_hash

        if calldata == []:
            calldata = [key_pair.public_key]

        address, salt = _new_address(
            class_hash=class_hash,
            calldata=calldata,
        )

        await prepay_account(
            address=address,
            eth_fee_contract=self.eth_fee_contract,
            strk_fee_contract=self.strk_fee_contract,
        )
        return address, key_pair, salt, class_hash


@pytest_asyncio.fixture(scope="package")
async def deploy_account_details_factory(
    account_with_validate_deploy_class_hash: int,
    eth_fee_contract: Contract,
    strk_fee_contract: Contract,
) -> AccountToBeDeployedDetailsFactory:
    """
    Returns AccountToBeDeployedDetailsFactory.

    The Factory's get() method returns: address, key_pair, salt
    and class_hash of the account with validate deploy.
    Prefunds the address with enough tokens to allow for deployment.
    """
    return AccountToBeDeployedDetailsFactory(
        class_hash=account_with_validate_deploy_class_hash,
        eth_fee_contract=eth_fee_contract,
        strk_fee_contract=strk_fee_contract,
    )


@pytest.fixture(scope="package")
def pre_deployed_account_with_validate_deploy(client) -> BaseAccount:
    """
    Returns an Account pre-deployed on specified network. Used to deploy other accounts.
    """

    address = DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS
    private_key = DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY

    return Account(
        address=address,
        client=client,
        key_pair=KeyPair.from_private_key(int(private_key, 16)),
        chain=StarknetChainId.SEPOLIA,
    )


@pytest_asyncio.fixture(scope="function")
async def argent_account_v040_data(
    eth_fee_contract: Contract,
    strk_fee_contract: Contract,
) -> AccountPrerequisites:
    key_pair = KeyPair.from_private_key(_get_random_private_key_unsafe())

    # Based on ABI definition documentation
    constructor_calldata = [
        0,
        key_pair.public_key,
        1,
    ]

    address, salt = _new_address(ARGENT_V040_CLASS_HASH, constructor_calldata)

    await prepay_account(
        address=address,
        eth_fee_contract=eth_fee_contract,
        strk_fee_contract=strk_fee_contract,
    )

    return AccountPrerequisites(address, salt, constructor_calldata, key_pair)


@pytest_asyncio.fixture(scope="package")
async def argent_account_v040(
    eth_fee_contract: Contract,
    strk_fee_contract: Contract,
    client,
) -> BaseAccount:
    key_pair = KeyPair.from_private_key(_get_random_private_key_unsafe())

    # Based on ABI definition documentation
    constructor_calldata = [
        0,
        key_pair.public_key,
        1,
    ]

    address, salt = _new_address(ARGENT_V040_CLASS_HASH, constructor_calldata)

    await prepay_account(
        address=address,
        eth_fee_contract=eth_fee_contract,
        strk_fee_contract=strk_fee_contract,
    )

    deploy_result = await Account.deploy_account_v3(
        address=address,
        class_hash=ARGENT_V040_CLASS_HASH,
        salt=salt,
        key_pair=key_pair,
        client=client,
        constructor_calldata=constructor_calldata,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    await deploy_result.wait_for_acceptance()
    return deploy_result.account
