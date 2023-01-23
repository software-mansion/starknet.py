from typing import List, Literal, TypedDict, Union

STRUCT_ENTRY = "struct"
FUNCTION_ENTRY = "function"
CONSTRUCTOR_ENTRY = "constructor"
L1_HANDLER_ENTRY = "l1_handler"
EVENT_ENTRY = "event"


class TypedMemberDict(TypedDict):
    name: str
    type: str


class StructMemberDict(TypedMemberDict):
    offset: int


class StructDict(TypedDict):
    type: Literal["struct"]
    name: str
    size: int
    members: List[StructMemberDict]


class FunctionBaseDict(TypedDict):
    name: str
    inputs: List[TypedMemberDict]
    outputs: List[TypedMemberDict]


class FunctionDict(FunctionBaseDict):
    type: Literal["function"]


class ConstructorDict(FunctionBaseDict):
    type: Literal["constructor"]


class L1HandlerDict(FunctionBaseDict):
    type: Literal["l1_handler"]


class EventDict(TypedDict):
    name: str
    type: Literal["event"]
    data: List[TypedMemberDict]
    keys: List[TypedMemberDict]


AbiDictEntry = Union[
    StructDict, FunctionDict, ConstructorDict, L1HandlerDict, EventDict
]
AbiDictList = List[AbiDictEntry]
