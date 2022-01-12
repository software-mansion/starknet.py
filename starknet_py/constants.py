import os
from enum import Enum


class TxStatus(Enum):
    RECEIVED = "RECEIVED"
    NOT_RECEIVED = "NOT_RECEIVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"


ACCEPTED_STATUSES = (TxStatus.ACCEPTED_ON_L1, TxStatus.ACCEPTED_ON_L2)

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "."))
DEFAULT_CPP_LIB_PATH = os.path.join(ROOT_DIR, "utils", "crypto")
