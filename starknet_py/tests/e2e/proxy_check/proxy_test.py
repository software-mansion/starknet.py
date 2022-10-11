import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.contract import Contract
from starknet_py.transactions.declare import make_declare_tx


async def put_and_get_map_contract(map_contract: Contract, key: int, val: int) -> int:
    """Put (key, val) into map_contract's storage and retrieve value under the key"""
    await (
        await map_contract.functions["put"].invoke(key, val, max_fee=int(1e16))
    ).wait_for_acceptance()
    (result,) = await map_contract.functions["get"].call(key=key)
    return result


@pytest.mark.asyncio
async def test_contract_from_address_no_proxy(
    gateway_account_client, map_compiled_contract
):
    deployment_result = await Contract.deploy(
        compiled_contract=map_compiled_contract,
        client=gateway_account_client,
    )
    await deployment_result.wait_for_acceptance()

    contract = await Contract.from_address(
        address=deployment_result.deployed_contract.address,
        client=gateway_account_client,
    )

    assert all(f in contract.functions for f in ("put", "get"))

    result = await put_and_get_map_contract(map_contract=contract, key=69, val=13)
    assert result == 13


@pytest.mark.asyncio
async def test_contract_from_address_with_proxy(
    gateway_account_client, compiled_proxy, map_compiled_contract
):
    declare_map_contract_tx = make_declare_tx(compiled_contract=map_compiled_contract)
    result_map = await gateway_account_client.declare(declare_map_contract_tx)

    implementation_key = (
        "implementation_hash"
        if "implementation_hash" in compiled_proxy
        else "implementation"
    )
    deployment_result = await Contract.deploy(
        compiled_contract=compiled_proxy,
        constructor_args={
            implementation_key: result_map.class_hash,
            "selector": get_selector_from_name("put"),
            "calldata_len": 2,
            "calldata": [69, 420],
        },
        client=gateway_account_client,
    )
    await deployment_result.wait_for_acceptance()

    proxy_contract = await Contract.from_address(
        address=deployment_result.deployed_contract.address,
        client=gateway_account_client,
    )
    proxied_contract = await Contract.from_address(
        address=deployment_result.deployed_contract.address,
        client=gateway_account_client,
        proxy_config=True,
    )

    assert all(f in proxied_contract.functions for f in ("put", "get"))
    assert proxied_contract.address == proxy_contract.address

    result = await put_and_get_map_contract(
        map_contract=proxied_contract, key=69, val=13
    )
    assert result == 13
