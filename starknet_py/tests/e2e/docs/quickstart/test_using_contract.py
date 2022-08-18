# pylint: disable=import-outside-toplevel, duplicate-code
import os
import pytest

directory = os.path.dirname(__file__)


@pytest.mark.asyncio
async def test_using_contract(gateway_client, gateway_account_client, map_contract):
    # pylint: disable=unused-variable,too-many-locals
    # add to docs: start
    from starknet_py.contract import Contract
    from starknet_py.net import AccountClient
    from starknet_py.net.networks import TESTNET
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.models import StarknetChainId

    client = GatewayClient(TESTNET)
    # add to docs: end
    client = gateway_client

    # add to docs: start

    acc_client = await AccountClient.create_account(
        gateway_client, chain=StarknetChainId.TESTNET
    )

    contract_address = (
        "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"
    )
    key = 1234
    # add to docs: end

    contract_address = map_contract.address
    # add to docs: start

    # Create contract from contract's address - Contract will download contract's ABI to know its interface.
    contract = await Contract.from_address(contract_address, gateway_account_client)
    # add to docs: end

    abi = contract.data.abi

    # add to docs: start

    # If the ABI is known, create the contract directly (this is the preferred way).
    contract = Contract(
        contract_address,
        abi,
        gateway_account_client,
    )

    # All exposed functions are available at contract.functions.
    # Here we invoke a function, creating a new transaction.
    invocation = await contract.functions["put"].invoke(key, 7, max_fee=int(1e16))

    # Invocation returns InvokeResult object. It exposes a helper for waiting until transaction is accepted.
    await invocation.wait_for_acceptance()

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["get"].call(key)
    # saved = 7 now
    # add to docs: end

    assert saved == 7
