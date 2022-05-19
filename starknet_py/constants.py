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

OZ_PROXY_STORAGE_KEY = get_storage_var_address("Proxy_implementation_address")
