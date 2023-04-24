import json

import pytest

from starknet_py.cairo.felt import decode_shortstring, encode_shortstring
from starknet_py.common import create_casm_class
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test_general_v1_interaction(gateway_account):
    # declare
    erc20_sierra = read_contract(
        "erc20_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    erc20_casm = read_contract(
        "erc20_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )

    casm_class_hash = compute_casm_class_hash(create_casm_class(erc20_casm))

    declare_tx = await gateway_account.sign_declare_v2_transaction(
        erc20_sierra, casm_class_hash, max_fee=MAX_FEE
    )
    resp = await gateway_account.client.declare(transaction=declare_tx)
    await gateway_account.client.wait_for_tx(resp.transaction_hash)

    deployer = Deployer()
    contract_deployment = deployer.create_contract_deployment(
        resp.class_hash,
        abi=json.loads(erc20_sierra)["abi"],
        cairo_version=1,
        calldata={
            "name_": encode_shortstring("erc20_basic"),
            "symbol_": encode_shortstring("ERC20B"),
            "decimals_": 10,
            "initial_supply": 12345,
            "recipient": gateway_account.address,
        },
    )

    deploy_invoke_transaction = await gateway_account.sign_invoke_transaction(
        calls=contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await gateway_account.client.send_transaction(deploy_invoke_transaction)
    await gateway_account.client.wait_for_tx(resp.transaction_hash)

    erc20 = Contract(
        address=contract_deployment.address,
        abi=json.loads(erc20_sierra)["abi"],
        provider=gateway_account,
        cairo_version=1,
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
    # declare
    bridge_sierra = read_contract(
        "token_bridge_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    bridge_casm = read_contract(
        "token_bridge_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )

    casm_class_hash = compute_casm_class_hash(create_casm_class(bridge_casm))

    declare_tx = await gateway_account.sign_declare_v2_transaction(
        bridge_sierra, casm_class_hash, max_fee=MAX_FEE
    )
    resp = await gateway_account.client.declare(transaction=declare_tx)
    await gateway_account.client.wait_for_tx(resp.transaction_hash)

    deployer = Deployer()
    contract_deployment = deployer.create_contract_deployment(
        resp.class_hash,
        abi=json.loads(bridge_sierra)["abi"],
        cairo_version=1,
        calldata={"governor_address": gateway_account.address},
    )

    deploy_invoke_transaction = await gateway_account.sign_invoke_transaction(
        calls=contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await gateway_account.client.send_transaction(deploy_invoke_transaction)
    await gateway_account.client.wait_for_tx(resp.transaction_hash)

    bridge = Contract(
        address=contract_deployment.address,
        abi=json.loads(bridge_sierra)["abi"],
        provider=gateway_account,
        cairo_version=1,
    )

    await (
        await bridge.functions["set_l1_bridge"].invoke(
            l1_bridge_address={"address": 0x11}, max_fee=MAX_FEE
        )
    ).wait_for_acceptance()
