from typing import Tuple, Optional, cast, Union, List, Dict

from starkware.crypto.signature.signature import get_random_private_key
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.definitions.fields import ContractAddressSalt

from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.contract import Contract, _unpack_client_and_account, DeployResult
from starknet_py.net import KeyPair, AccountClient
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.networks import Network
from starknet_py.transactions.deploy import make_deploy_tx

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
    priv_key = get_random_private_key()
    key_pair = KeyPair.from_private_key(priv_key)
    salt = ContractAddressSalt.get_random_value()

    address = calculate_contract_address_from_hash(
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
        raise ValueError("One of network or client must be provided")

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


async def deploy(
    *,
    account: Optional[BaseAccount] = None,
    compilation_source: Optional[StarknetCompilationSource] = None,
    compiled_contract: Optional[str] = None,
    constructor_args: Optional[Union[List, Dict]] = None,
    salt: Optional[int] = None,
    search_paths: Optional[List[str]] = None,
    client: Optional[Client] = None,
) -> DeployAccount:
    # pylint: disable=too-many-arguments
    """
    Deploys a contract and waits until it has ``PENDING`` status.
    Either `compilation_source` or `compiled_contract` is required.

    :param client: Client
    :param compilation_source: string containing source code or a list of source files paths
    :param compiled_contract: string containing compiled contract. Useful for reading compiled contract from a file.
    :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
    :param salt: Optional salt. Random value is selected if it is not provided.
    :param search_paths: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts.
    :raises: `ValueError` if neither compilation_source nor compiled_contract is provided.
    :return: DeployResult instance

    .. deprecated:: 0.8.0
        This metodh has been deprecated in favor of deploying through cairo syscall.
    """
    client, account = _unpack_client_and_account(client, account)

    compiled = create_compiled_contract(
        compilation_source, compiled_contract, search_paths
    )
    # pylint: disable=protected-access
    translated_args = Contract._translate_constructor_args(compiled, constructor_args)
    deploy_tx = make_deploy_tx(
        compiled_contract=compiled,
        constructor_calldata=translated_args,
        salt=salt,
    )
    res = await client.deploy(deploy_tx)
    contract_address = res.contract_address

    if account is not None:
        deployed_contract = Contract(
            account=account,
            address=contract_address,
            abi=compiled.abi,
        )
    else:
        deployed_contract = Contract(
            client=client,
            address=contract_address,
            abi=compiled.abi,
        )

    deploy_result = DeployResult(
        hash=res.transaction_hash,
        _client=client,
        deployed_contract=deployed_contract,
    )

    return deploy_result
