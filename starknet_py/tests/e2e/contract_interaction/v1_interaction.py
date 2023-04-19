import json

import pytest

from starknet_py.cairo.felt import decode_shortstring, encode_shortstring
from starknet_py.common import create_casm_class
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test1(network):
    account = Account(
        address=0x7D2F37B75A5E779F7DA01C22ACEE1B66C39E8BA470EE5448F05E1462AFCEDB4,
        client=GatewayClient(net=network),
        key_pair=KeyPair.from_private_key(0xCD613E30D8F16ADF91B7584A2265B1F5),
        chain=StarknetChainId.TESTNET,
    )
    # declare
    erc20_compiled_sierra = read_contract(
        "erc20_compiled.json", directory=CONTRACTS_COMPILED_DIR / "precompiled"
    )
    erc20_compiled_casm = read_contract(
        "erc20_compiled.casm", directory=CONTRACTS_COMPILED_DIR / "precompiled"
    )

    casm_class = create_casm_class(erc20_compiled_casm)
    casm_class_hash = compute_casm_class_hash(casm_class)

    declare_tx = await account.sign_declare_v2_transaction(
        erc20_compiled_sierra, casm_class_hash, max_fee=MAX_FEE
    )

    resp = await account.client.declare(transaction=declare_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    class_hash = resp.class_hash

    deployer = Deployer()

    contract_deployment = deployer.create_contract_deployment_raw(
        class_hash,
        raw_calldata=[
            encode_shortstring("erc20_basic"),
            encode_shortstring("ERC20B"),
            10,
            1000000000,
            1000,
            account.address,
        ],
    )

    deploy_invoke_transaction = await account.sign_invoke_transaction(
        calls=contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    erc20_address = contract_deployment.address

    erc20 = Contract(
        address=erc20_address,
        abi=json.loads(erc20_compiled_sierra)["abi"],
        provider=account,
        cairo_version=1,
    )

    decoded = decode_shortstring((await erc20.functions["get_name"].call())[0])

    decimals = await erc20.functions["get_decimals"].call()

    supply = await erc20.functions["get_total_supply"].call()

    account_balance = await erc20.functions["balance_of"].call(account=account.address)

    resp = await erc20.functions["transfer_from"].invoke(
        sender=account.address, recipient=0x11, amount=10, max_fee=MAX_FEE
    )
    await resp.wait_for_acceptance()

    fake_balance = await erc20.functions["balance_of"].call(account=0x11)

    print("abc")
