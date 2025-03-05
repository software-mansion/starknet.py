from typing import Tuple

import pytest
import pytest_asyncio

from starknet_py.cairo.felt import decode_shortstring
from starknet_py.contract import Contract, DeclareResult, DeployResult
from starknet_py.hash.storage import get_storage_var_address
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract

U128_MAX = (1 << 128) - 1
U256_MAX = (1 << 256) - 1


@pytest_asyncio.fixture(scope="package")
async def declare_deploy_hello2(account) -> Tuple[DeclareResult, DeployResult]:
    contract = load_contract(contract_name="Hello2", version=ContractVersion.V2)

    declare_result = await Contract.declare_v3(
        account=account,
        compiled_contract=contract["sierra"],
        compiled_contract_casm=contract["casm"],
        # TODO(#1558): Use auto estimation
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await declare_result.wait_for_acceptance()

    deploy_result = await declare_result.deploy_v3(
        # TODO(#1558): Use auto estimation
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await deploy_result.wait_for_acceptance()

    return declare_result, deploy_result


@pytest_asyncio.fixture(scope="package", name="contract")
# pylint: disable=redefined-outer-name
async def hello2_contract(declare_deploy_hello2) -> Contract:
    _, deploy_result = declare_deploy_hello2
    return deploy_result.deployed_contract


@pytest.mark.asyncio
async def test_deploy_cairo2(contract):
    assert isinstance(contract, Contract)


@pytest.mark.asyncio
async def test_cairo2_interaction(contract):
    # TODO(#1558): Use auto estimation
    invoke_res = await contract.functions["increase_balance"].invoke_v3(
        amount=100, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()

    # TODO (#1558): Use auto estimation
    invoke_res = await contract.functions["increase_balance"].invoke_v3(
        amount=100, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()

    (balance,) = await contract.functions["get_balance"].call()
    assert balance == 200


@pytest.mark.asyncio
async def test_cairo2_interaction2(contract):
    # TODO (#1558): Use auto estimation
    invoke_res = await contract.functions["increase_balance_u8"].invoke_v3(
        255, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()

    (balance,) = await contract.functions["get_balance_u8"].call()
    assert balance == 255


@pytest.mark.asyncio
@pytest.mark.parametrize("uint_bits", [16, 32, 64, 128, 256])
async def test_cairo2_uint(contract, uint_bits):
    (result,) = await contract.functions[f"test_u{uint_bits}"].call(255)
    assert result == 256


@pytest.mark.asyncio
async def test_cairo2_u256(contract):
    (result,) = await contract.functions["test_u256"].call(p1=U256_MAX - 1)
    assert result == U256_MAX

    (result,) = await contract.functions["test_u256"].call(
        p1={"low": U128_MAX - 1, "high": U128_MAX}
    )
    assert result == U256_MAX


@pytest.mark.asyncio
async def test_cairo2_contract_address(contract):
    # TODO (#1558): Use auto estimation
    invoke_res = await contract.functions["set_ca"].invoke_v3(
        address=contract.account.address, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()

    (result,) = await contract.functions["get_ca"].call()
    assert result == contract.account.address


@pytest.mark.asyncio
async def test_cairo2_interaction3(contract):
    # TODO (#1558): Use auto estimation
    invoke_res = await contract.functions["increase_balance"].invoke_v3(
        100, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()
    (balance,) = await contract.functions["get_balance"].call()
    key = get_storage_var_address("balance")
    storage = await contract.client.get_storage_at(contract.address, key)
    assert storage == balance

    # TODO (#1558): Use auto estimation
    invoke_res = await contract.functions["set_ca"].invoke_v3(
        contract.account.address, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()
    (ca,) = await contract.functions["get_ca"].call()  # pylint: disable=invalid-name
    key = get_storage_var_address("ca")
    storage = await contract.client.get_storage_at(contract.address, key)
    assert storage == ca

    # TODO (#1558): Use auto estimation
    invoke_res = await contract.functions["set_status"].invoke_v3(
        True, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()
    (status,) = await contract.functions["get_status"].call()
    key = get_storage_var_address("status")
    storage = await contract.client.get_storage_at(contract.address, key)
    assert storage == status

    invoke_res = await contract.functions["set_user1"].invoke_v3(
        {
            "address": contract.account.address,
            "is_claimed": True,
        },
        # TODO (#1558): Use auto estimation
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await invoke_res.wait_for_acceptance()
    (user1,) = await contract.functions["get_user1"].call()
    key = get_storage_var_address("user1")
    storage1 = await contract.client.get_storage_at(contract.address, key)
    storage2 = await contract.client.get_storage_at(contract.address, key + 1)
    assert storage1 == user1["address"]
    assert storage2 == user1["is_claimed"]


@pytest.mark.asyncio
async def test_cairo2_echo(contract):
    (result,) = await contract.functions["echo_un_tuple"].call((77, 123))
    assert result == (77, 123)

    (result,) = await contract.functions["echo_array_u256"].call([123, 55, 77, 255])
    assert result == [123, 55, 77, 255]

    (result,) = await contract.functions["echo_array_bool"].call(
        [True, True, False, False]
    )
    assert result == [True, True, False, False]


@pytest.mark.asyncio
async def test_cairo2_echo_struct(contract):
    (result,) = await contract.functions["echo_struct"].call({"val": "simple"})
    assert decode_shortstring(result["val"]) == "simple"


@pytest.mark.asyncio
async def test_cairo2_echo_complex_struct(contract):
    # TODO (#1558): Use auto estimation
    invoke_result = await contract.functions["set_bet"].invoke_v3(
        resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_result.wait_for_acceptance()

    (bet,) = await contract.functions["get_bet"].call(1)

    assert bet == {
        "name": 1952805748,
        "description": 6579555,
        "expire_date": 1,
        "creation_time": 1,
        "creator": contract.account.address,
        "is_cancelled": False,
        "is_voted": False,
        "bettor": {
            "address": contract.account.address,
            "is_claimed": False,
        },
        "counter_bettor": {
            "address": contract.account.address,
            "is_claimed": False,
        },
        "winner": False,
        "pool": 10,
        "amount": 1000,
    }


@pytest.mark.asyncio
async def test_cairo2_echo_tuple(contract):
    (result,) = await contract.functions["array_bool_tuple"].call([1, 2, 3], True)
    assert result == ([1, 2, 3, 1, 2], True)

    (result,) = await contract.functions["tuple_echo"].call(([1, 2, 3], [4, 5, 6]))
    assert result == ([1, 2, 3], [4, 5, 6])
