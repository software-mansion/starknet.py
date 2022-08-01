import asyncio
import os
from pathlib import Path

import pytest

from starknet_py.contract import Contract

MAX_FEE = int(1e20)

COMPILED_PROXY_SOURCES = ["argent_proxy_compiled.json", "argent_proxy_compiled.json"]


@pytest.mark.asyncio
async def test_contract_from_address_throws_on_proxy_cycle(gateway_account_client):
    for compiled_proxy in COMPILED_PROXY_SOURCES:
        compiled_proxy = (
            Path(os.path.dirname(__file__)) / "../mock_contracts_dir" / compiled_proxy
        ).read_text("utf-8")
        proxy1_deployment = await Contract.deploy(
            compiled_contract=compiled_proxy,
            constructor_args=[0x123],
            client=gateway_account_client,
        )
        proxy2_deployment = await Contract.deploy(
            compiled_contract=compiled_proxy,
            constructor_args=[0x123],
            client=gateway_account_client,
        )
        await proxy1_deployment.wait_for_acceptance()
        await proxy2_deployment.wait_for_acceptance()

        proxy1 = proxy1_deployment.deployed_contract
        proxy2 = proxy2_deployment.deployed_contract

        argent_proxy = "_set_implementation" in proxy1.functions

        if argent_proxy:
            await proxy1.functions["_set_implementation"].invoke(
                implementation=proxy2.address, max_fee=MAX_FEE
            )
            await proxy2.functions["_set_implementation"].invoke(
                implementation=proxy1.address, max_fee=MAX_FEE
            )
        else:
            await proxy1.functions["_set_implementation_hash"].invoke(
                new_implementation=proxy2.address, max_fee=MAX_FEE
            )
            await proxy2.functions["_set_implementation_hash"].invoke(
                new_implementation=proxy1.address, max_fee=MAX_FEE
            )

        await asyncio.sleep(2000)

        with pytest.raises(RecursionError) as exinfo:
            await Contract.from_address(
                address=proxy2_deployment.deployed_contract.address,
                client=gateway_account_client,
                proxy_config=True,
            )

        assert "Proxy cycle detected" in str(exinfo.value)
