import pytest


@pytest.mark.asyncio
async def test_using_contract():
    # pylint: disable=import-outside-toplevel
    from starknet_py.contract import Contract
    from starknet_py.net.client import Client
    from starknet_py.net.networks import TESTNET

    client = Client(TESTNET)
    key = 1234

    # Create contract from contract's address - Contract will download contract's ABI to know its interface.
    contract = await Contract.from_address(
        "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", client
    )

    abi = contract.data.abi

    # If the ABI is known, create the contract directly (this is the preferred way).
    contract = Contract(
        "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b",
        abi,
        client,
    )

    # All exposed functions are available at contract.functions.
    # Here we invoke a function, creating a new transaction.
    invocation = await contract.functions["set_value"].invoke(key, 7, max_fee=0)

    # Invocation returns InvokeResult object. It exposes a helper for waiting until transaction is accepted.
    await invocation.wait_for_acceptance()

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["get_value"].call(key)
    # saved = 7 now

    assert saved == 7
