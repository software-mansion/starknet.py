import pytest


@pytest.mark.asyncio
async def test_resolving_proxies(
    gateway_client, map_contract, deploy_proxy_to_contract_oz_argent
):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.contract import Contract

    # docs: end
    address = map_contract.address
    # docs: start
    # If the contract is not a proxy just pass its address and a client
    contract = await Contract.from_address(address=address, client=gateway_client)

    # docs: end
    address = deploy_proxy_to_contract_oz_argent.deployed_contract.address
    # docs: start
    # However, if you have a proxy and want to use it as a regular contract,
    # you will have to pass one more argument
    # It will check if your proxy is OpenZeppelin or ArgentX proxy
    # To resolve other proxies pass custom ProxyCheck as proxy_config parameter
    contract = await Contract.from_address(
        address=address, client=gateway_client, proxy_config=True
    )

    # After that contract can be used as usual
    # docs: end

    assert contract is not None
