import pytest


@pytest.mark.asyncio
async def test_handling_client_errors(gateway_account_client):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.contract import Contract
    from starknet_py.net.client_errors import ClientError
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.networks import TESTNET

    try:
        contract_address = "1"  # Doesn't exist
        client = GatewayClient(TESTNET)
        # docs: end
        client = gateway_account_client
        # docs: start
        await Contract.from_address(contract_address, client)
    except ClientError as error:
        print(error.code, error.message)
    # docs: end
