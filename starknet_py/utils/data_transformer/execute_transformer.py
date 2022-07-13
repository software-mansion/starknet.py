from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet_py.utils.data_transformer import FunctionCallSerializer

abi = [
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

execute_transformer = FunctionCallSerializer(
    abi=abi[0], identifier_manager=identifier_manager_from_abi(abi)
)
