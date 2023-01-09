import pytest


@pytest.mark.asyncio
async def test_handling_client_errors(gateway_account):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.client.http.errors import ClientError
    from starknet_py.contract.contract import Contract

    try:
        contract_address = "1"  # Doesn't exist
        # docs: end
        account = gateway_account
        # docs: start
        await Contract.from_address(address=contract_address, provider=account)
    except ClientError as error:
        print(error.code, error.message)
    # docs: end
