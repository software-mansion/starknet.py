import random
from typing import Optional, Tuple, cast

from starknet_py.constants import EC_ORDER
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.client import Client
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.networks import Network

AccountToBeDeployedDetails = Tuple[int, KeyPair, int, int]
MAX_FEE = int(1e20)


async def get_deploy_account_details(
    *, class_hash: int, fee_contract: Contract
) -> AccountToBeDeployedDetails:
    """
    Returns address, key_pair, salt and class_hash of the account with validate deploy.

    :param class_hash: Class hash of account to be deployed
    :param fee_contract: Contract for prefunding deployments
    """
    priv_key = _get_random_private_key_unsafe()
    key_pair = KeyPair.from_private_key(priv_key)
    salt = 1

    address = compute_address(
        salt=salt,
        class_hash=class_hash,
        constructor_calldata=[key_pair.public_key],
        deployer_address=0,
    )

    res = await fee_contract.functions["transfer"].invoke(
        recipient=address, amount=int(1e15), max_fee=MAX_FEE
    )
    await res.wait_for_acceptance()

    return address, key_pair, salt, class_hash


async def get_deploy_account_transaction(
    *,
    address: int,
    key_pair: KeyPair,
    salt: int,
    class_hash: int,
    network: Optional[Network] = None,
    client: Optional[Client] = None,
) -> DeployAccount:
    """
    Get a signed DeployAccount transaction from provided details
    """
    if network is None and client is None:
        raise ValueError("One of network or client must be provided.")

    account = AccountClient(
        address=address,
        client=client
        or GatewayClient(
            net=cast(
                Network, network
            )  # Cast needed because pyright doesn't recognize network as not None at this point
        ),
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


def _get_random_private_key_unsafe() -> int:
    """
    Returns a private key in the range [1, EC_ORDER).
    This is not a safe way of generating private keys and should be used only in tests.
    """
    return random.randint(1, EC_ORDER - 1)
