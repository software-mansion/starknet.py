import pytest
from starkware.starknet.public.abi import (
    get_storage_var_address,
)

from starknet_py.contract import Contract
from starknet_py.net.client_errors import ContractNotFoundError
from starknet_py.proxy_check import ProxyResolutionError, ProxyCheck


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
@pytest.mark.parametrize(
    "deploy_proxy_to_contract",
    [
        ("oz_proxy_compiled.json", "map_compiled.json"),
        ("argent_proxy_compiled.json", "map_compiled.json"),
    ],
    indirect=True,
)
async def test_contract_from_address_with_proxy(
    gateway_account_client, deploy_proxy_to_contract
):
    proxy_contract = await Contract.from_address(
        address=deploy_proxy_to_contract.deployed_contract.address,
        client=gateway_account_client,
    )
    proxied_contract = await Contract.from_address(
        address=deploy_proxy_to_contract.deployed_contract.address,
        client=gateway_account_client,
        proxy_config=True,
    )

    assert all(f in proxied_contract.functions for f in ("put", "get"))
    assert proxied_contract.address == proxy_contract.address

    result = await put_and_get_map_contract(
        map_contract=proxied_contract, key=69, val=13
    )
    assert result == 13


@pytest.mark.asyncio
async def test_contract_from_address_unsupported_client(rpc_account_client):
    with pytest.raises(TypeError, match=r".only supports GatewayClient."):
        await Contract.from_address(
            address=123,
            client=rpc_account_client,
        )


@pytest.mark.asyncio
async def test_contract_from_invalid_address(gateway_account_client):
    with pytest.raises(ContractNotFoundError):
        await Contract.from_address(
            address=123,
            client=gateway_account_client,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "deploy_proxy_to_contract",
    [("oz_proxy_custom_compiled.json", "map_compiled.json")],
    indirect=True,
)
async def test_contract_from_address_invalid_proxy_checks(
    gateway_account_client, deploy_proxy_to_contract
):
    with pytest.raises(ProxyResolutionError):
        await Contract.from_address(
            address=deploy_proxy_to_contract.deployed_contract.address,
            client=gateway_account_client,
            proxy_config=True,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "deploy_proxy_to_contract",
    [("oz_proxy_custom_compiled.json", "map_compiled.json")],
    indirect=True,
)
async def test_contract_from_address_custom_proxy_check(
    gateway_account_client, deploy_proxy_to_contract
):
    class CustomProxyCheck(ProxyCheck):
        async def is_proxy(self, contract: "Contract") -> bool:
            return False

        async def implementation(self, contract: "Contract") -> int:
            return await contract.client.get_storage_at(
                contract_address=contract.address,
                key=get_storage_var_address("Proxy_implementation_hash_custom"),
                block_hash="latest",
            )

    await Contract.from_address(
        address=deploy_proxy_to_contract.deployed_contract.address,
        client=gateway_account_client,
        proxy_config={"proxy_checks": [CustomProxyCheck()]},
    )


@pytest.mark.asyncio
async def test_contract_from_address_with_old_address_proxy(
    gateway_account_client, old_proxy, map_compiled_contract
):
    map_deployment_result = await Contract.deploy(
        compiled_contract=map_compiled_contract,
        client=gateway_account_client,
    )
    await map_deployment_result.wait_for_acceptance()

    deployment_result = await Contract.deploy(
        compiled_contract=old_proxy,
        constructor_args={
            "implementation_address": map_deployment_result.deployed_contract.address
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
