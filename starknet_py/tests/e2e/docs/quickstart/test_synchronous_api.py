import pytest


@pytest.mark.asyncio
def test_synchronous_api():
    # pylint: disable=import-outside-toplevel
    from starknet_py.contract import Contract
    from starknet_py.net.client import Client

    key = 1234
    # pylint: disable=no-member
    contract = Contract.from_address_sync(
        "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b",
        Client("testnet"),
    )
    invocation = contract.functions["set_value"].invoke_sync(key, 7, max_fee=0)
    invocation.wait_for_acceptance_sync()

    (saved,) = contract.functions["get_value"].call_sync(key)  # 7

    assert saved == 7
