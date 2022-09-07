from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet_py.utils.data_transformer import FunctionCallSerializer

abi_v0 = [
    {
        "inputs": [
            {"name": "call_array_len", "type": "felt"},
            {"name": "call_array", "type": "CallArray*"},
            {"name": "calldata_len", "type": "felt"},
            {"name": "calldata", "type": "felt*"},
            {"name": "nonce", "type": "felt"},
        ],
        "name": "__execute__",
        "outputs": [
            {"name": "retdata_size", "type": "felt"},
            {"name": "retdata", "type": "felt*"},
        ],
        "type": "function",
    },
    {
        "members": [
            {"name": "to", "offset": 0, "type": "felt"},
            {"name": "selector", "offset": 1, "type": "felt"},
            {"name": "data_offset", "offset": 2, "type": "felt"},
            {"name": "data_len", "offset": 3, "type": "felt"},
        ],
        "name": "CallArray",
        "size": 4,
        "type": "struct",
    },
]

abi_v1 = [
    {
        "inputs": [
            {"name": "call_array_len", "type": "felt"},
            {"name": "call_array", "type": "CallArray*"},
            {"name": "calldata_len", "type": "felt"},
            {"name": "calldata", "type": "felt*"},
        ],
        "name": "__execute__",
        "outputs": [
            {"name": "retdata_size", "type": "felt"},
            {"name": "retdata", "type": "felt*"},
        ],
        "type": "function",
    },
    {
        "members": [
            {"name": "to", "offset": 0, "type": "felt"},
            {"name": "selector", "offset": 1, "type": "felt"},
            {"name": "data_offset", "offset": 2, "type": "felt"},
            {"name": "data_len", "offset": 3, "type": "felt"},
        ],
        "name": "CallArray",
        "size": 4,
        "type": "struct",
    },
]

abi = abi_v0

execute_transformer = FunctionCallSerializer(
    abi=abi_v0[0], identifier_manager=identifier_manager_from_abi(abi_v0)
)

execute_transformer_v1 = FunctionCallSerializer(
    abi=abi_v1[0], identifier_manager=identifier_manager_from_abi(abi_v1)
)


def execute_transformer_by_version(version: int) -> FunctionCallSerializer:
    mapping = {0: execute_transformer, 1: execute_transformer_v1}
    return mapping[version]
