from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionStatus,
)

TxStatus = TransactionStatus

ACCEPTED_STATUSES = (TxStatus.ACCEPTED_ON_L1, TxStatus.ACCEPTED_ON_L2)

# Address came from starkware-libs/starknet-addresses repository: https://github.com/starkware-libs/starknet-addresses
FEE_CONTRACT_ADDRESS = (
    "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
)

DEFAULT_DEPLOYER_ADDRESS = (
    "0x041a78e741e5aF2fEc34B695679bC6891742439f7AFB8484Ecd7766661aD02BF"
)

RPC_INVALID_MESSAGE_SELECTOR_ERROR = 21
RPC_CLASS_HASH_NOT_FOUND_ERROR = 28
