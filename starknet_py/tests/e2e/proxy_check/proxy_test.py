import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.utils import deploy

MAX_FEE = int(1e20)


@pytest.mark.asyncio
async def test_argent_contract_from_address_throws_on_too_many_steps(
    map_contract, compiled_proxy, new_account
):
    proxy1_deployment = await deploy(
        compiled_contract=compiled_proxy,
        constructor_args=[map_contract.address],
        account=new_account,
    )
    proxy2_deployment = await deploy(
        compiled_contract=compiled_proxy,
        constructor_args=[proxy1_deployment.deployed_contract.address],
        account=new_account,
    )

    await proxy1_deployment.wait_for_acceptance()
    await proxy2_deployment.wait_for_acceptance()

    with pytest.raises(RecursionError) as exinfo:
        await Contract.from_address(
            proxy2_deployment.deployed_contract.address,
            proxy_config={"max_steps": 2},
            account=new_account,
        )

    assert "Max number of steps exceeded" in str(exinfo.value)


async def set_implementation(proxy1: Contract, proxy2: Contract):
    argent_proxy = "_set_implementation" in proxy1.functions
    set_implementation_name = (
        "_set_implementation" if argent_proxy else "_set_implementation_hash"
    )
    implementation = "implementation" if argent_proxy else "new_implementation"

    params = {
        "proxy1": {implementation: proxy2.address},
        "proxy2": {implementation: proxy1.address},
    }

    await (
        await proxy1.functions[set_implementation_name].invoke(
            **params["proxy2"], max_fee=MAX_FEE
        )
    ).wait_for_acceptance()
    await (
        await proxy2.functions[set_implementation_name].invoke(
            **params["proxy1"], max_fee=MAX_FEE
        )
    ).wait_for_acceptance()


@pytest.mark.asyncio
async def test_contract_from_address_throws_on_proxy_cycle(compiled_proxy, new_account):
    proxy1_deployment = await deploy(
        compiled_contract=compiled_proxy,
        constructor_args=[0x123],
        account=new_account,
    )
    proxy2_deployment = await deploy(
        compiled_contract=compiled_proxy,
        constructor_args=[0x123],
        account=new_account,
    )
    await proxy1_deployment.wait_for_acceptance()
    await proxy2_deployment.wait_for_acceptance()

    proxy1 = proxy1_deployment.deployed_contract
    proxy2 = proxy2_deployment.deployed_contract

    await set_implementation(proxy1, proxy2)

    with pytest.raises(RecursionError) as exinfo:
        await Contract.from_address(
            address=proxy2_deployment.deployed_contract.address,
            proxy_config=True,
            account=new_account,
        )

    assert "Proxy cycle detected" in str(exinfo.value)


@pytest.mark.asyncio
async def test_contract_from_address_with_1_proxy(
    map_contract, compiled_proxy, new_account
):
    deployment_result = await deploy(
        compiled_contract=compiled_proxy,
        constructor_args=[map_contract.address],
        account=new_account,
    )
    await deployment_result.wait_for_acceptance()

    proxy_contract = await Contract.from_address(
        deployment_result.deployed_contract.address,
        proxy_config=True,
        account=new_account,
    )

    assert all(f in proxy_contract.functions for f in ("put", "get"))


@pytest.mark.asyncio
async def test_contract_from_address_with_2_proxy(
    map_contract, compiled_proxy, new_account
):
    proxy1_deployment = await deploy(
        compiled_contract=compiled_proxy,
        constructor_args=[map_contract.address],
        account=new_account,
    )
    proxy2_deployment = await deploy(
        compiled_contract=compiled_proxy,
        constructor_args=[proxy1_deployment.deployed_contract.address],
        account=new_account,
    )

    await proxy1_deployment.wait_for_acceptance()
    await proxy2_deployment.wait_for_acceptance()

    proxy_contract = await Contract.from_address(
        proxy2_deployment.deployed_contract.address,
        proxy_config=True,
        account=new_account,
    )

    assert all(f in proxy_contract.functions for f in ("put", "get"))
