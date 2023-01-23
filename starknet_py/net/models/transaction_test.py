import re
import typing
from typing import cast

from starkware.starknet.services.api.contract_class import ContractClass

from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import (
    Declare,
    DeclareSchema,
    compute_invoke_hash,
)


def test_invoke_hash():
    for selector in [
        "increase_balance",
        1530486729947006463063166157847785599120665941190480211966374137237989315360,
    ]:
        assert (
            compute_invoke_hash(
                entry_point_selector=selector,
                contract_address=0x03606DB92E563E41F4A590BC01C243E8178E9BA8C980F8E464579F862DA3537C,
                calldata=[1234],
                chain_id=StarknetChainId.TESTNET,
                version=0,
                max_fee=0,
            )
            == 0xD0A52D6E77B836613B9F709AD7F4A88297697FEFBEF1ADA3C59692FF46702C
        )


def test_declare_compress_program(balance_contract):
    contract_class = ContractClass.loads(balance_contract)
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
