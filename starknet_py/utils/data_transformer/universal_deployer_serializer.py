from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet_py.utils.data_transformer import FunctionCallSerializer

universal_deployer_abi = [
    {
        "inputs": [
            {"name": "class_hash", "type": "felt"},
            {"name": "salt", "type": "felt"},
            {"name": "unique", "type": "felt"},
            {"name": "constructor_calldata_len", "type": "felt"},
            {"name": "constructor_calldata", "type": "felt*"},
        ],
        "name": "deployContract",
        "outputs": [{"name": "contract_address", "type": "felt"}],
        "type": "function",
    }
]

universal_deployer_serializer = FunctionCallSerializer(
    abi=universal_deployer_abi[0],
    identifier_manager=identifier_manager_from_abi(abi=universal_deployer_abi),
)
