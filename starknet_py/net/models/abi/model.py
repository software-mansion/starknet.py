from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Optional
from starknet_py.cairo.data_types import StructType, CairoType


@dataclass
class Abi:
    @dataclass
    class Function:
        name: str
        inputs: OrderedDict[str, CairoType]
        outputs: OrderedDict[str, CairoType]

    @dataclass
    class Event:
        name: str
        data: OrderedDict[str, CairoType]

    defined_structures: Dict[str, StructType]
    functions: Dict[str, Function]
    constructor: Optional[Function]
    l1_handler: Optional[Function]
    events: Dict[str, Event]
