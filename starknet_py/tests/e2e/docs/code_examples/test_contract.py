# pylint: disable=unused-variable
import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import InvokeTransactionV3, ResourceBounds
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import DeclareV2, DeclareV3, StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract


def test_init():
    # docs-start: init
    contract = Contract(
        address=0x123,
        abi=[
            {
                "inputs": [{"name": "amount", "type": "felt"}],
                "name": "increase_balance",
                "outputs": [],
                "type": "function",
            },
        ],
        provider=Account(
            address=0x321,
            client=FullNodeClient(node_url="your.node.url"),
            key_pair=KeyPair(12, 34),
            chain=StarknetChainId.SEPOLIA,
        ),
        cairo_version=0,
    )
    # docs-end: init


@pytest.mark.asyncio
async def test_from_address(account, contract_address):
    # docs-start: from_address
    address = 1 or 0x1 or "0x1"
    # docs-end: from_address
    address = contract_address
    # docs-start: from_address
    contract = await Contract.from_address(address=address, provider=account)
    # or if the contract is a proxy (read more about resolving proxies in the `Guide`)
    config = True
    # docs-end: from_address
    config = False
    # docs-start: from_address
    contract = await Contract.from_address(
        address=address, provider=account, proxy_config=config
    )
    # docs-end: from_address


@pytest.mark.asyncio
async def test_declare_v2(account):
    compiled_contract = load_contract(
        contract_name="TestContract", version=ContractVersion.V1
    )
    # docs-start: declare_v2
    # here `compiled_contract` is a dict containing sierra and casm artifacts
    declare_result = await Contract.declare_v2(
        account,
        compiled_contract=compiled_contract["sierra"],
        compiled_contract_casm=compiled_contract["casm"],
        max_fee=int(1e15),
    )
    # docs-end: declare_v2
    await declare_result.wait_for_acceptance()

    assert isinstance(declare_result.declare_transaction, DeclareV2)
    assert isinstance(declare_result.hash, int)
    assert isinstance(declare_result.class_hash, int)
    assert declare_result.compiled_contract == compiled_contract["sierra"]


@pytest.mark.asyncio
async def test_declare_v3(account):
    contract = load_contract(contract_name="TestContract", version=ContractVersion.V2)
    # docs-start: declare_v3
    # here `contract` is a dict containing sierra and casm artifacts
    declare_result = await Contract.declare_v3(
        account,
        compiled_contract=contract["sierra"],
        compiled_contract_casm=contract["casm"],
        l1_resource_bounds=ResourceBounds(
            max_amount=int(1e5), max_price_per_unit=int(1e13)
        ),
    )
    # docs-end: declare_v3
    await declare_result.wait_for_acceptance()

    assert isinstance(declare_result.declare_transaction, DeclareV3)
    assert isinstance(declare_result.hash, int)
    assert isinstance(declare_result.class_hash, int)
    assert declare_result.compiled_contract == contract["sierra"]


@pytest.mark.asyncio
async def test_deploy_contract_v1(account, class_hash):
    # docs-start: deploy_contract_v1
    deploy_result = await Contract.deploy_contract_v1(
        account=account,
        class_hash=class_hash,
        abi=[
            {
                "inputs": [{"name": "amount", "type": "felt"}],
                "name": "increase_balance",
                "outputs": [],
                "type": "function",
            }
        ],
        max_fee=int(1e15),
    )
    # or when contract has a constructor with arguments
    deploy_result = await Contract.deploy_contract_v1(
        account=account,
        class_hash=class_hash,
        abi=[
            {
                "inputs": [{"name": "value", "type": "felt"}],
                "name": "constructor",
                "outputs": [],
                "type": "constructor",
            },
        ],
        constructor_args={"value": 1},
        max_fee=int(1e15),
    )
    # docs-end: deploy_contract_v1


@pytest.mark.asyncio
async def test_deploy_contract_v3(account, cairo1_hello_starknet_class_hash: int):
    compiled_contract = load_contract("HelloStarknet")["sierra"]
    # docs-start: deploy_contract_v3
    abi = create_sierra_compiled_contract(
        compiled_contract=compiled_contract
    ).parsed_abi
    # docs-end: deploy_contract_v3
    class_hash = cairo1_hello_starknet_class_hash
    # docs-start: deploy_contract_v3
    deploy_result = await Contract.deploy_contract_v3(
        class_hash=class_hash,
        account=account,
        abi=abi,
        l1_resource_bounds=ResourceBounds(
            max_amount=int(1e5), max_price_per_unit=int(1e13)
        ),
    )
    # docs-end: deploy_contract_v3
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract
    assert isinstance(contract.address, int)
    assert len(contract.functions) != 0

    transaction = await account.client.get_transaction(tx_hash=deploy_result.hash)
    assert isinstance(transaction, InvokeTransactionV3)

    class_hash = await account.client.get_class_hash_at(
        contract_address=contract.address
    )
    assert class_hash == cairo1_hello_starknet_class_hash
