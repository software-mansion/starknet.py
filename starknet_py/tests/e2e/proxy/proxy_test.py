from typing import Tuple, List

import pytest
from starkware.starknet.public.abi import get_storage_var_address

from starknet_py.contract import Contract
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ContractNotFoundError
from starknet_py.net.client_models import Abi
from starknet_py.net.models import Address
from starknet_py.proxy.contract_abi_resolver import AbiNotFoundError
from starknet_py.proxy.proxy_check import (
    ArgentProxyCheck,
    OpenZeppelinProxyCheck,
)
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


async def is_map_working_properly(map_contract: Contract, key: int, val: int) -> bool:
    """Put (key, val) into map_contract's storage and check if value under the key is val"""
    await (
        await map_contract.functions["put"].invoke(key, val, max_fee=int(1e16))
    ).wait_for_acceptance()
    (result,) = await map_contract.functions["get"].call(key=key)
    return result == val


@pytest.mark.asyncio
async def test_contract_from_address_no_proxy(account_client, map_contract):
    contract = await Contract.from_address(
        address=map_contract.address,
        client=account_client,
    )

    assert contract.functions.keys() == {"put", "get"}
    assert contract.address == map_contract.address
    assert await is_map_working_properly(map_contract=contract, key=69, val=13)


@pytest.mark.asyncio
async def test_contract_from_address_with_proxy(
    account_client, deploy_proxy_to_contract_oz_argent
):
    proxy_contract = await Contract.from_address(
        address=deploy_proxy_to_contract_oz_argent.deployed_contract.address,
        client=account_client,
    )
    proxied_contract = await Contract.from_address(
        address=deploy_proxy_to_contract_oz_argent.deployed_contract.address,
        client=account_client,
        get_implementation_func=True,
    )

    assert proxied_contract.functions.keys() == {"put", "get"}
    assert proxied_contract.address == proxy_contract.address
    assert await is_map_working_properly(map_contract=proxied_contract, key=69, val=13)


@pytest.mark.asyncio
async def test_contract_from_invalid_address(account_client):
    with pytest.raises(ContractNotFoundError):
        await Contract.from_address(
            address=123,
            client=account_client,
        )


@pytest.mark.asyncio
async def test_contract_from_address_unsupported_proxy(
    account_client, deploy_proxy_to_contract_custom
):
    with pytest.raises(AbiNotFoundError):
        await Contract.from_address(
            address=deploy_proxy_to_contract_custom.deployed_contract.address,
            client=account_client,
            get_implementation_func=True,
        )


@pytest.mark.asyncio
async def test_contract_from_address_custom_func(
    account_client, deploy_proxy_to_contract_custom
):
    async def custom_get_implementation_func(
        proxy_abi: Abi,  # pylint: disable=unused-argument
        proxy_address: Address,
        client: Client,
    ) -> Tuple[List[int], List[int]]:
        storage_var_implementation = await client.get_storage_at(
            contract_address=proxy_address,
            key=get_storage_var_address("Proxy_implementation_hash_custom"),
            block_hash="latest",
        )
        return [], [storage_var_implementation]

    contract = await Contract.from_address(
        address=deploy_proxy_to_contract_custom.deployed_contract.address,
        client=account_client,
        get_implementation_func=custom_get_implementation_func,
    )

    assert contract.functions.keys() == {"put", "get"}
    assert contract.address == deploy_proxy_to_contract_custom.deployed_contract.address
    assert await is_map_working_properly(map_contract=contract, key=69, val=13)


@pytest.mark.asyncio
async def test_contract_from_address_two_implementations(
    account_client, deploy_proxy_to_contract_multiple_vars
):
    with pytest.raises(AbiNotFoundError):
        await Contract.from_address(
            address=deploy_proxy_to_contract_multiple_vars.deployed_contract.address,
            client=account_client,
            get_implementation_func=True,
        )


@pytest.mark.asyncio
async def test_contract_from_address_with_old_address_proxy(
    new_account_client, old_proxy, map_contract
):
    account_client = new_account_client
    declare_result = await Contract.declare(
        account=account_client, compiled_contract=old_proxy, max_fee=MAX_FEE
    )
    await declare_result.wait_for_acceptance()
    deploy_result = await declare_result.deploy(
        constructor_args={"implementation_address": map_contract.address},
        max_fee=MAX_FEE,
    )
    await deploy_result.wait_for_acceptance()

    proxy_contract = await Contract.from_address(
        address=deploy_result.deployed_contract.address,
        client=account_client,
    )
    proxied_contract = await Contract.from_address(
        address=deploy_result.deployed_contract.address,
        client=account_client,
        proxy_config=True,
    )

    assert proxied_contract.functions.keys() == {"put", "get"}
    assert proxied_contract.address == proxy_contract.address
    assert await is_map_working_properly(map_contract=proxied_contract, key=69, val=13)


@pytest.mark.parametrize("proxy_check_cls", [ArgentProxyCheck, OpenZeppelinProxyCheck])
def test_proxy_config_deprecation_warning(proxy_check_cls):
    with pytest.warns(
        DeprecationWarning,
        match=r"ProxyCheck is deprecated and will be removed in the future.",
    ):
        _ = proxy_check_cls()
