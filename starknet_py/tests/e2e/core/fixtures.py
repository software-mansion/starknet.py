# pylint: disable=redefined-outer-name
import pytest
import pytest_asyncio

from starknet_py.common import create_compiled_contract
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.account.account_deployment_result import AccountDeploymentResult
from starknet_py.net.client_models import DeclareTransactionResponse
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract
from starknet_py.tests.e2e.utils import _get_random_private_key_unsafe


@pytest.fixture(scope="package")
def core_gateway_client() -> GatewayClient:
    return GatewayClient(net="https://external.integration.starknet.io")


@pytest.fixture(scope="package")
def core_pre_deployed_account(core_gateway_client) -> Account:
    return Account(
        address=0x4D402AD11563556F5E3AF2695B640C772B516B4C4634294C1562460979BC1B1,
        client=core_gateway_client,
        key_pair=KeyPair.from_private_key(9999),
        chain=StarknetChainId.TESTNET,
    )


async def declare_contract(
    file_name: str, account: Account
) -> DeclareTransactionResponse:
    compiled_contract = read_contract(file_name)

    declare_tx = await account.sign_declare_transaction(
        compiled_contract, max_fee=MAX_FEE
    )
    resp = await account.client.declare(declare_tx)

    return resp


@pytest_asyncio.fixture(scope="package")
async def core_declare_account_response(
    core_pre_deployed_account,
) -> DeclareTransactionResponse:
    resp = await declare_contract(
        "account_with_validate_deploy_compiled.json", core_pre_deployed_account
    )
    await core_pre_deployed_account.client.wait_for_tx(resp.transaction_hash)
    return resp


@pytest_asyncio.fixture(scope="package")
async def core_declare_map_response(
    core_pre_deployed_account,
) -> DeclareTransactionResponse:
    resp = await declare_contract("map_compiled.json", core_pre_deployed_account)
    await core_pre_deployed_account.client.wait_for_tx(resp.transaction_hash)
    return resp


@pytest_asyncio.fixture(scope="package")
async def core_deploy_account_response(
    core_declare_account_response, core_fee_contract, core_gateway_client
) -> AccountDeploymentResult:
    class_hash = core_declare_account_response.class_hash
    private_key = _get_random_private_key_unsafe()
    key_pair = KeyPair.from_private_key(private_key)
    salt = 1

    address = compute_address(
        class_hash=class_hash,
        constructor_calldata=[key_pair.public_key],
        salt=salt,
        deployer_address=0,
    )

    invoke_resp = await core_fee_contract.functions["transfer"].invoke(
        recipient=address, amount=int(1e15), max_fee=MAX_FEE
    )
    await invoke_resp.wait_for_acceptance()

    deploy_result = await Account.deploy_account(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=core_gateway_client,
        chain=StarknetChainId.TESTNET,
        max_fee=int(1e15),
    )

    return deploy_result


@pytest_asyncio.fixture(scope="package")
async def core_account(
    core_deploy_account_response: AccountDeploymentResult,
) -> Account:
    await core_deploy_account_response.wait_for_acceptance()

    return core_deploy_account_response.account


@pytest.fixture(scope="package")
def core_fee_contract(core_pre_deployed_account: Account) -> Contract:
    """
    Returns an instance of the fee contract. It is used to transfer tokens.
    """
    abi = [
        {
            "inputs": [
                {"name": "recipient", "type": "felt"},
                {"name": "amount", "type": "Uint256"},
            ],
            "name": "transfer",
            "outputs": [{"name": "success", "type": "felt"}],
            "type": "function",
        },
        {
            "members": [
                {"name": "low", "offset": 0, "type": "felt"},
                {"name": "high", "offset": 1, "type": "felt"},
            ],
            "name": "Uint256",
            "size": 2,
            "type": "struct",
        },
    ]

    return Contract(
        address=FEE_CONTRACT_ADDRESS,
        abi=abi,
        provider=core_pre_deployed_account,
    )


@pytest_asyncio.fixture(scope="package")
async def core_map_contract(
    core_pre_deployed_account: Account,
    core_declare_map_response: DeclareTransactionResponse,
):
    deployer = Deployer()
    call, address = deployer.create_deployment_call(
        core_declare_map_response.class_hash
    )

    resp = await core_pre_deployed_account.execute(call, max_fee=MAX_FEE)
    await core_pre_deployed_account.client.wait_for_tx(resp.transaction_hash)

    abi = create_compiled_contract(
        compiled_contract=read_contract("map_compiled.json")
    ).abi

    return Contract(address, abi, core_pre_deployed_account)
