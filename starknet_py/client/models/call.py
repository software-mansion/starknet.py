from dataclasses import dataclass
from typing import Iterable, List, Union


@dataclass
class Call:
    to_addr: int
    selector: int
    calldata: List[int]


Calls = Union[Call, Iterable[Call]]
