import re
import typing
from typing import cast

import pytest

from starknet_py.common import (
    create_compiled_contract,
    create_contract_class,
    create_sierra_compiled_contract,
)
from starknet_py.net.client_models import TransactionType
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import (
    Declare,
    DeclareSchema,
    DeclareV2,
    DeployAccount,
    Invoke,
    InvokeSchema,
    compute_invoke_hash,
)
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


def test_invoke_hash():
    for selector in [
        "increase_balance",
        1530486729947006463063166157847785599120665941190480211966374137237989315360,
    ]:
        assert (
            compute_invoke_hash(
                entry_point_selector=selector,
                sender_address=0x03606DB92E563E41F4A590BC01C243E8178E9BA8C980F8E464579F862DA3537C,
                calldata=[1234],
                chain_id=StarknetChainId.TESTNET,
                version=0,
                max_fee=0,
            )
            == 0xD0A52D6E77B836613B9F709AD7F4A88297697FEFBEF1ADA3C59692FF46702C
        )


def test_declare_compress_program(balance_contract):
    contract_class = create_contract_class(balance_contract)
    declare_transaction = Declare(
        contract_class=contract_class,
        sender_address=0x1234,
        max_fee=0x1111,
        nonce=0x1,
        signature=[0x1, 0x2],
        version=1,
    )

    schema = DeclareSchema()

    serialized = typing.cast(dict, schema.dump(declare_transaction))
    # Pattern used in match taken from
    # https://github.com/starkware-libs/starknet-specs/blob/df8cfb3da309f3d5dd08d804961e5a9ab8774945/api/starknet_api_openrpc.json#L1943
    assert re.match(
        r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$",
        serialized["contract_class"]["program"],
    )

    deserialized = cast(Declare, schema.load(serialized))
    assert deserialized.contract_class == contract_class


compiled_contract = read_contract("erc20_compiled.json")
sierra_compiled_contract = read_contract(
    "minimal_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
)


@pytest.mark.parametrize(
    "transaction, calculated_hash",
    [
        (
            Invoke(
                sender_address=0x1,
                calldata=[1, 2, 3],
                max_fee=10000,
                signature=[],
                nonce=23,
                version=1,
            ),
            3484767022419258107070028252604380065385354331198975073942248877262069264133,
        ),
        (
            DeployAccount(
                class_hash=0x1,
                contract_address_salt=0x2,
                constructor_calldata=[1, 2, 3, 4],
                max_fee=10000,
                signature=[],
                nonce=23,
                version=1,
            ),
            1258460340144554539989794559757396219553018532617589681714052999991876798273,
        ),
        (
            Declare(
                contract_class=create_compiled_contract(
                    compiled_contract=compiled_contract
                ),
                sender_address=123,
                max_fee=10000,
                signature=[],
                nonce=23,
                version=1,
            ),
            1040693415700027927754435936502603457316156159253336216524207357712582758611,
        ),
        (
            DeclareV2(
                contract_class=create_sierra_compiled_contract(
                    compiled_contract=sierra_compiled_contract
                ),
                compiled_class_hash=0x1,
                max_fee=1000,
                nonce=20,
                sender_address=0x1234,
                signature=[0x1, 0x2],
                version=2,
            ),
            669407379128146207315662195646033049577214993241551268214610074015474911988,
        ),
    ],
)
def test_calculate_transaction_hash(transaction, calculated_hash):
    assert (
        transaction.calculate_hash(chain_id=StarknetChainId.TESTNET) == calculated_hash
    )


def test_serialize_deserialize_invoke():
    data = {
        "sender_address": "0x1",
        "calldata": ["0x1", "0x2", "0x3"],
        "max_fee": "0x1",
        "signature": [],
        "nonce": "0x1",
        "version": "0x1",
        "type": "INVOKE_FUNCTION",
    }
    invoke = InvokeSchema().load(data)
    serialized_invoke = InvokeSchema().dump(invoke)

    assert isinstance(invoke, Invoke)
    assert invoke.type == TransactionType.INVOKE
    assert isinstance(serialized_invoke, dict)
    assert serialized_invoke["type"] == "INVOKE_FUNCTION"
