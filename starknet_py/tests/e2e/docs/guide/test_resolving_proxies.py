from typing import Optional

import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net.client import Client
from starknet_py.net.client_models import Call
from starknet_py.net.models import Address
from starknet_py.proxy.contract_abi_resolver import ProxyConfig
from starknet_py.proxy.proxy_check import ProxyCheck, ArgentProxyCheck, OpenZeppelinProxyCheck


@pytest.mark.asyncio
async def test_resolving_proxies(
    gateway_client, map_contract, deploy_proxy_to_contract_exposed, deploy_proxy_to_contract_oz_argent
):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.contract import Contract

    # docs: end
    address = map_contract.address
    # docs: start
    # Getting the direct contract from address
    contract = await Contract.from_address(address=address, client=gateway_client)

    # docs: end
    address = deploy_proxy_to_contract_oz_argent.deployed_contract.address
    # docs: start
    # To use contract behind a proxy as a regular contract, set proxy_config to True
    # It will check if your proxy is OpenZeppelin or ArgentX proxy
    contract = await Contract.from_address(
        address=address, client=gateway_client, proxy_config=True
    )

    # After that contract can be used as usual

    # To resolve proxy contract other than OpenZeppelin or ArgentX, a custom ProxyCheck is needed
    # It should be a subclass of ProxyCheck and have methods:
    # - implementation_address - returns address of the proxied implementation or None
    # - implementation_hash - returns class_hash of the proxied implementation or None

    # The ProxyCheck below resolves proxy contracts which have implementation
    # stored in implementation() function as address
    class CustomProxyCheck(ProxyCheck):
        async def implementation_address(
            self, address: Address, client: Client
        ) -> Optional[int]:
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

    # docs: end
    address = deploy_proxy_to_contract_exposed.deployed_contract.address
    # docs: start
    contract = await Contract.from_address(
        address=address, client=gateway_client, proxy_config=proxy_config
    )
    # docs: end

    assert contract.functions.keys() == {"put", "get"}
