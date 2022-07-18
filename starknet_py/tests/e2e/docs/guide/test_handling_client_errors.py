import pytest


@pytest.mark.asyncio
async def test_handling_client_errors(account_client):
    # pylint: disable=import-outside-toplevel
    # add to docs: start
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.networks import TESTNET
    from starknet_py.net.client_errors import ContractNotFoundError
    from starknet_py.contract import Contract

    try:
        contract_address = "1"  # Doesn't exist
        client = GatewayClient(TESTNET)
        # add to docs: end
        client = account_client
        # add to docs: start
        await Contract.from_address(contract_address, client)
    except ContractNotFoundError as error:
        print(error.code, error.message)
    # add to docs: end
