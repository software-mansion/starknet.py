from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionStatus,
)
from starkware.starknet.public.abi import get_storage_var_address

TxStatus = TransactionStatus

ACCEPTED_STATUSES = (TxStatus.ACCEPTED_ON_L1, TxStatus.ACCEPTED_ON_L2)

OZ_PROXY_STORAGE_KEY = get_storage_var_address("Proxy_implementation_address")
