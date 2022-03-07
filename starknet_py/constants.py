import os
from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionStatus,
)

TxStatus = TransactionStatus

ACCEPTED_STATUSES = (TxStatus.ACCEPTED_ON_L1, TxStatus.ACCEPTED_ON_L2)

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "."))
DEFAULT_CPP_LIB_PATH = os.path.join(ROOT_DIR, "utils", "crypto")
