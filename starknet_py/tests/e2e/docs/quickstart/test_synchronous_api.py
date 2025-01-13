# pylint: disable=import-outside-toplevel, no-member, duplicate-code
from starknet_py.net.client_models import ResourceBounds


def test_synchronous_api(account, map_contract):
    # docs: start
    from starknet_py.contract import Contract

    contract_address = (
        "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"
    )
    # docs: end

    contract_address = map_contract.address

    # docs: start

    key = 1234
    contract = Contract.from_address_sync(address=contract_address, provider=account)

    invocation = contract.functions["put"].invoke_v3_sync(
        key,
        7,
        l1_resource_bounds=ResourceBounds(
            max_amount=int(1e5), max_price_per_unit=int(1e13)
        ),
    )
    invocation.wait_for_acceptance_sync()

    (saved,) = contract.functions["get"].call_sync(key)  # 7
    # docs: end

    assert saved == 7
