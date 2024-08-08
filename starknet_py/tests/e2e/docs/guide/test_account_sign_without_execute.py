import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.models.transaction import DeclareV2, DeployAccountV1, InvokeV1


@pytest.mark.asyncio
async def test_account_sign_without_execute(
    account, sierra_minimal_compiled_contract_and_class_hash
):
    # pylint: disable=import-outside-toplevel
    assert isinstance(account, Account)
    address = selector = class_hash = salt = 0x1
    calldata = []
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash
    max_fee = 100000

    # docs: start
    from starknet_py.net.client_models import Call

    # Create a signed Invoke transaction
    call = Call(to_addr=address, selector=selector, calldata=calldata)
    invoke_transaction = await account.sign_invoke_v1(call, max_fee=max_fee)

    # Create a signed Declare transaction
    declare_transaction = await account.sign_declare_v2(
        compiled_contract,
        compiled_class_hash=compiled_class_hash,
        auto_estimate=True,
    )

    # Create a signed DeployAccount transaction
    deploy_account_transaction = await account.sign_deploy_account_v1(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=calldata,
        max_fee=max_fee,
    )
    # docs: end

    assert isinstance(invoke_transaction, InvokeV1)
    assert isinstance(declare_transaction, DeclareV2)
    assert isinstance(deploy_account_transaction, DeployAccountV1)
