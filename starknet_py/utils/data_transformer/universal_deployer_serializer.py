from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet_py.utils.data_transformer.data_transformer import CairoSerializer

universal_deployer_abi = [
    {
        "data": [
            {"name": "address", "type": "felt"},
            {"name": "deployer", "type": "felt"},
            {"name": "unique", "type": "felt"},
            {"name": "classHash", "type": "felt"},
            {"name": "calldata_len", "type": "felt"},
            {"name": "calldata", "type": "felt*"},
            {"name": "salt", "type": "felt"},
        ],
        "keys": [],
        "name": "ContractDeployed",
        "type": "event",
    },
    {
        "inputs": [
            {"name": "classHash", "type": "felt"},
            {"name": "salt", "type": "felt"},
            {"name": "unique", "type": "felt"},
            {"name": "calldata_len", "type": "felt"},
            {"name": "calldata", "type": "felt*"},
        ],
        "name": "deployContract",
        "outputs": [{"name": "address", "type": "felt"}],
        "type": "function",
    },
]

deploy_contract_event_abi = universal_deployer_abi[0]
deploy_contract_abi = universal_deployer_abi[1]

universal_deployer_serializer = CairoSerializer(
    identifier_manager=identifier_manager_from_abi(abi=universal_deployer_abi),
)
