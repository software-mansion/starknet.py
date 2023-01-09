from dataclasses import dataclass
from typing import List


@dataclass
class Event:
    """
    Dataclass representing an event emitted by transaction
    """

    from_address: int
    keys: List[int]
    data: List[int]
