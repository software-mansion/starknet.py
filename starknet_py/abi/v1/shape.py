from typing import List, Literal, Optional, TypedDict, Union

ENUM_ENTRY = "enum"
STRUCT_ENTRY = "struct"
FUNCTION_ENTRY = "function"
EVENT_ENTRY = "event"


class TypeDict(TypedDict):
    type: str


class TypedMemberDict(TypeDict):
    name: str


class StructDict(TypedDict):
    type: Literal["struct"]
    name: str
    members: List[TypedMemberDict]


class FunctionBaseDict(TypedDict):
    name: str
    inputs: List[TypedMemberDict]
    outputs: List[TypeDict]
    state_mutability: Optional[Literal["external", "view"]]


class FunctionDict(FunctionBaseDict):
    type: Literal["function"]


class EventDict(TypedDict):
    name: str
    type: Literal["event"]
    inputs: List[TypedMemberDict]


class EnumDict(TypedDict):
    type: Literal["enum"]
    name: str
    variants: List[TypedMemberDict]


AbiDictEntry = Union[StructDict, FunctionDict, EventDict, EnumDict]
AbiDictList = List[AbiDictEntry]
