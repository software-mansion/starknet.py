import re
import typing
from typing import cast

from starknet_py.common import create_contract_class
from starknet_py.net.client_models import TransactionType
from starknet_py.net.models.transaction import (
    Declare,
    DeclareSchema,
    Invoke,
    InvokeSchema,
)
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


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
    "minimal_contract_compiled.json", directory=CONTRACTS_COMPILED_V2_DIR
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
