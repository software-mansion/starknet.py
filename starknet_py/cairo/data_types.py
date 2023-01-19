from __future__ import annotations

from abc import ABC
from collections import OrderedDict
from dataclasses import dataclass
from typing import List


class CairoType(ABC):
    """
    Base type for all Cairo type representations. All types extend it.
    """


@dataclass
class FeltType(CairoType):
    """
    Type representation of Cairo field element.
    """


@dataclass
class TupleType(CairoType):
    """
    Type representation of Cairo tuples without named fields.
    """

    types: List[CairoType]  #: types of every tuple element.


@dataclass
class NamedTupleType(CairoType):
    """
    Type representation of Cairo tuples with named fields.
    """

    types: OrderedDict[str, CairoType]  #: types of every tuple member.


@dataclass
class ArrayType(CairoType):
    """
    Type representation of Cairo arrays.
    """

    inner_type: CairoType  #: type of element inside array.


@dataclass
class StructType(CairoType):
    """
    Type representation of Cairo structures.
    """

    name: str  #: Structure name
    # We need ordered dict, because it is important in serialization
    types: OrderedDict[str, CairoType]  #: types of every structure member.
