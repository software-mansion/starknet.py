from typing import Optional

import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net.client import Client
from starknet_py.net.client_models import Call
from starknet_py.net.models import Address
from starknet_py.proxy.contract_abi_resolver import ProxyConfig
from starknet_py.proxy.proxy_check import (
    ArgentProxyCheck,
    OpenZeppelinProxyCheck,
    ProxyCheck,
)


@pytest.mark.asyncio
async def test_resolving_proxies(
    gateway_client,
    map_contract,
    deploy_proxy_to_contract_exposed,
    deploy_proxy_to_contract_oz_argent,
):
    # pylint: disable=import-outside-toplevel
    # docs-1: start
    from starknet_py.contract import Contract

    # docs-1: end
    address = map_contract.address
    # docs-1: start
    # Getting the direct contract from address
    contract = await Contract.from_address(address=address, client=gateway_client)

    # docs-1: end
    address = deploy_proxy_to_contract_oz_argent.deployed_contract.address
    # docs-1: start
    # To use contract behind a proxy as a regular contract, set proxy_config to True
    # It will check if your proxy is OpenZeppelin or ArgentX proxy
    contract = await Contract.from_address(
        address=address, client=gateway_client, proxy_config=True
    )

    # After that contract can be used as usual
    # docs-1: end
    # docs-2: start
    # To resolve proxy contract other than OpenZeppelin or ArgentX, a custom ProxyCheck is needed
    # The ProxyCheck below resolves proxy contracts which have implementation
    # stored in implementation() function as address
    class CustomProxyCheck(ProxyCheck):
        async def implementation_address(
            self, address: Address, client: Client
        ) -> Optional[int]:
            # Note that None is returned, since our custom Proxy uses
            # the address of another contract as implementation and not the class hash
            return None

        async def implementation_hash(
            self, address: Address, client: Client
        ) -> Optional[int]:
            call = Call(
                to_addr=address,
                selector=get_selector_from_name("implementation"),
                calldata=[],
            )
            (implementation,) = await client.call_contract(call=call)
            return implementation

    # Create ProxyConfig with the CustomProxyCheck
    proxy_config = ProxyConfig(proxy_checks=[CustomProxyCheck()])

    # More ProxyCheck instances can be passed to proxy_checks for it to be flexible
    proxy_config = ProxyConfig(
        proxy_checks=[CustomProxyCheck(), ArgentProxyCheck(), OpenZeppelinProxyCheck()]
    )

    # docs-2: end
    address = deploy_proxy_to_contract_exposed.deployed_contract.address
    # docs-2: start
    contract = await Contract.from_address(
        address=address, client=gateway_client, proxy_config=proxy_config
    )
    # docs-2: end

    assert contract.functions.keys() == {"put", "get"}
