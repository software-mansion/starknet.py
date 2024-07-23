from starknet_py.net.client_models import TransactionType
from starknet_py.net.models.transaction import InvokeV1, InvokeV1Schema


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
    invoke = InvokeV1Schema().load(data)
    serialized_invoke = InvokeV1Schema().dump(invoke)

    assert isinstance(invoke, InvokeV1)
    assert invoke.type == TransactionType.INVOKE
    assert isinstance(serialized_invoke, dict)
    assert serialized_invoke["type"] == "INVOKE_FUNCTION"
