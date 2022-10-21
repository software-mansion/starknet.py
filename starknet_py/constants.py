from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionStatus,
)
from starkware.starknet.public.abi import get_storage_var_address

TxStatus = TransactionStatus

ACCEPTED_STATUSES = (TxStatus.ACCEPTED_ON_L1, TxStatus.ACCEPTED_ON_L2)

# Address came from starkware-libs/starknet-addresses repository: https://github.com/starkware-libs/starknet-addresses
FEE_CONTRACT_ADDRESS = (
    "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
)

# Address came from starknet-devnet docs https://shard-labs.github.io/starknet-devnet/docs/guide/mint-token
DEVNET_FEE_CONTRACT_ADDRESS = (
    "0x62230ea046a9a5fbc261ac77d03c8d41e5d442db2284587570ab46455fd2488"
)

OZ_PROXY_STORAGE_KEY = get_storage_var_address("Proxy_implementation_hash")
