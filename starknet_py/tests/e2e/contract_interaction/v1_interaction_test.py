import pytest

from starknet_py.cairo.felt import decode_shortstring, encode_shortstring
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.tests.e2e.fixtures.contracts import deploy_v1_contract


@pytest.mark.asyncio
async def test_general_v1_interaction(gateway_account):
    erc20 = await deploy_v1_contract(
        account=gateway_account,
        contract_file_name="erc20",
        calldata={
            "name_": encode_shortstring("erc20_basic"),
            "symbol_": encode_shortstring("ERC20B"),
            "decimals_": 10,
            "initial_supply": 12345,
            "recipient": gateway_account.address,
        },
    )

    decoded_name = decode_shortstring((await erc20.functions["get_name"].call())[0])
    (decimals,) = await erc20.functions["get_decimals"].call()
    (supply,) = await erc20.functions["get_total_supply"].call()
    (account_balance,) = await erc20.functions["balance_of"].call(
        account=gateway_account.address
    )

    await (
        await erc20.functions["transfer"].invoke(
            recipient=0x11, amount=10, max_fee=MAX_FEE
        )
    ).wait_for_acceptance()

    (after_transfer_balance,) = await erc20.functions["balance_of"].call(
        account=gateway_account.address
    )

    assert "erc20_basic" in decoded_name
    assert decimals == 10
    assert supply == 12345
    assert account_balance == 12345
    assert after_transfer_balance == 12345 - 10


@pytest.mark.asyncio
async def test_serializing_struct(gateway_account):
    bridge = await deploy_v1_contract(
        account=gateway_account,
        contract_file_name="token_bridge",
        calldata={"governor_address": gateway_account.address},
    )

    await (
        await bridge.functions["set_l1_bridge"].invoke(
            l1_bridge_address={"address": 0x11}, max_fee=MAX_FEE
        )
    ).wait_for_acceptance()
