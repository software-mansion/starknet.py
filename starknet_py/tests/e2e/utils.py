import random
from typing import List, Tuple

from starknet_py.constants import EC_ORDER
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.client import Client
from starknet_py.net.http_client import HttpClient, HttpMethod
from starknet_py.net.models import DeployAccountV3, StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.udc_deployer.deployer import _get_random_salt
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS

AccountToBeDeployedDetails = Tuple[int, KeyPair, int, int]


def _new_address(
    class_hash: int,
    calldata: List[int],
):
    salt = _get_random_salt()
    return (
        compute_address(
            salt=salt,
            class_hash=class_hash,
            constructor_calldata=calldata,
            deployer_address=0,
        ),
        salt,
    )


async def prepay_account(
    *,
    address: int,
    eth_fee_contract: Contract,
    strk_fee_contract: Contract,
):
    """
    Transfer fees from system contracts (ETH and STRK) to address specified.

    :param address: Address of the account to send funds to.
    :param eth_fee_contract: Contract for prefunding deployments in ETH.
    :param strk_fee_contract: Contract for prefunding deployments in STRK.
    """
    transfer_wei_res = await eth_fee_contract.functions["transfer"].invoke_v3(
        recipient=address, amount=int(1e40), resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await transfer_wei_res.wait_for_acceptance()

    transfer_fri_res = await strk_fee_contract.functions["transfer"].invoke_v3(
        recipient=address, amount=int(1e40), resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await transfer_fri_res.wait_for_acceptance()


async def get_deploy_account_transaction(
    *, address: int, key_pair: KeyPair, salt: int, class_hash: int, client: Client
) -> DeployAccountV3:
    """
    Get a signed DeployAccount transaction from provided details
    """

    account = Account(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA,
    )
    return await account.sign_deploy_account_v3(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )


def _get_random_private_key_unsafe() -> int:
    """
    Returns a private key in the range [1, EC_ORDER).
    This is not a safe way of generating private keys and should be used only in tests.
    """
    return random.randint(1, EC_ORDER - 1)


async def create_empty_block(http_client: HttpClient) -> None:
    url = http_client.url[:-4] if http_client.url.endswith("/rpc") else http_client.url
    await http_client.request(
        address=f"{url}/create_block",
        http_method=HttpMethod.POST,
    )
