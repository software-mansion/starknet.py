from dataclasses import dataclass
from typing import List, Optional


@dataclass
class L1toL2Message:
    """
    Dataclass representing a L1->L2 message
    """

    payload: List[int]
    l1_address: int
    l2_address: Optional[int] = None


@dataclass
class L2toL1Message:
    """
    Dataclass representing a L2->L1 message
    """

    payload: List[int]
    l1_address: int
    l2_address: Optional[int] = None
