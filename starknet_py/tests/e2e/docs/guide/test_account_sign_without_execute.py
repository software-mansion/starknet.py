import pytest

from starknet_py.net.models import Invoke
from starknet_py.net.models.transaction import Declare, DeployAccount


@pytest.mark.asyncio
async def test_account_sign_without_execute(account):
    # pylint: disable=import-outside-toplevel
    address = selector = class_hash = salt = 0x1
    calldata = []
    compiled_contract = ""
    max_fee = 100000

    # docs: start
    from starknet_py.net.client_models import Call

    # Create a signed Invoke transaction
    call = Call(to_addr=address, selector=selector, calldata=calldata)
    invoke_transaction = await account.sign_invoke_transaction(call, max_fee=max_fee)

    # Create a signed Declare transaction
    declare_transaction = await account.sign_declare_transaction(
        compiled_contract=compiled_contract, max_fee=max_fee
    )

    # Create a signed DeployAccount transaction
    deploy_account_transaction = await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=calldata,
        max_fee=max_fee,
    )
    # docs: end

    assert isinstance(invoke_transaction, Invoke)
    assert isinstance(declare_transaction, Declare)
    assert isinstance(deploy_account_transaction, DeployAccount)
