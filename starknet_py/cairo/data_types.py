from __future__ import annotations

from abc import ABC
from collections import OrderedDict
from dataclasses import dataclass
from typing import List, Union


class CairoType(ABC):
    pass


@dataclass
class FeltType(CairoType):
    pass


@dataclass
class TupleType(CairoType):
    types: List[CairoType]


@dataclass
class NamedTupleType(CairoType):
    types: OrderedDict[str, CairoType]


@dataclass
class ArrayType(CairoType):
    inner_type: CairoType


@dataclass
class StructType(CairoType):
    name: str
    # We need ordered dict, because it is important in serialization
    types: OrderedDict[str, CairoType]


# Inline type is one that can be used inline. For instance (a: felt, b: felt*, c: (felt, felt)).
InlineType = Union[FeltType, ArrayType, TupleType, NamedTupleType]
