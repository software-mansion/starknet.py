import dataclasses
from abc import abstractmethod, ABC
from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum, auto
from typing import List, Optional, Sequence, Iterator

add_backward_compatibility_space_ctx_var: ContextVar[int] = ContextVar(
    "add_backward_compatibility_space", default=False
)


class AstNode(ABC):
    @abstractmethod
    def get_children(self) -> Sequence[Optional["AstNode"]]:
        """
        Returns a list of the node's children (notes are not included).
        """

    def get_subtree(self) -> Iterator["AstNode"]:
        """
        Returns an iterator of all non-None nodes in the subtree rooted at this node, preorder
        (visit each node before its children).
        """
        yield self
        for child in filter(None, self.get_children()):
            yield from child.get_subtree()


@contextmanager
def add_backward_compatibility_space(value: bool):
    """
    Adds space before the colon when formatting named tuple types.
    This should be used for backward compatibility in the contract hash computation in versions
    before 0.10.0.
    For example, use "(a : felt)" instead of "(a: felt)".
    """
    token = add_backward_compatibility_space_ctx_var.set(value)
    try:
        yield
    finally:
        add_backward_compatibility_space_ctx_var.reset(token)


class CairoType(AstNode):
    def get_pointer_type(self) -> "CairoType":
        """
        Returns a type of a pointer to the current type.
        """
        return TypePointer(pointee=self)


@dataclasses.dataclass
class TypeFelt(CairoType):
    def get_children(self) -> Sequence[Optional[AstNode]]:
        return []


@dataclasses.dataclass
class TypeCodeoffset(CairoType):

    def get_children(self) -> Sequence[Optional[AstNode]]:
        return []


@dataclasses.dataclass
class TypePointer(CairoType):
    pointee: CairoType

    def get_children(self) -> Sequence[Optional[AstNode]]:
        return [self.pointee]


@dataclasses.dataclass
class TypeIdentifier(CairoType):
    """
    Represents a name of an unresolved type.
    This type can be resolved to TypeStruct or TypeDefinition.
    """

    name: str

    def get_children(self) -> Sequence[Optional[AstNode]]:
        return []


@dataclasses.dataclass
class TypeStruct(CairoType):
    scope: str

    def get_children(self) -> Sequence[Optional[AstNode]]:
        return []


@dataclasses.dataclass
class TypeFunction(CairoType):
    """
    Represents a type of a function.
    """

    scope: str

    def get_children(self) -> Sequence[Optional[AstNode]]:
        return []


@dataclasses.dataclass
class TypeTuple(CairoType):
    """
    Represents a type of a named or unnamed tuple.
    For example, "(felt, felt*)" or "(a: felt, b: felt*)".
    """

    @dataclasses.dataclass
    class Item(AstNode):
        """
        Represents a possibly named type item of a TypeTuple.
        For example: "felt" or "a: felt".
        """

        name: Optional[str]
        typ: CairoType

        def get_children(self) -> Sequence[Optional[AstNode]]:
            return [self.typ]

    members: List["TypeTuple.Item"]
    has_trailing_comma: bool = dataclasses.field(hash=False, compare=False)

    def get_children(self) -> Sequence[Optional[AstNode]]:
        return self.members

    @property
    def types(self) -> List[CairoType]:
        """
        Returns the unnamed types of the tuple.
        """
        return [x.typ for x in self.members]

    @classmethod
    def unnamed(cls, types: List[CairoType]):
        """
        Creates an unnamed tuple type from the given types.
        """
        return cls.from_members(
            members=[TypeTuple.Item(name=None, typ=typ) for typ in types],
        )

    @classmethod
    def from_members(cls, members: List["TypeTuple.Item"]):
        """
        Creates a tuple (with no notes) from the given members.
        """
        return cls(
            members=members,
            has_trailing_comma=False,
        )

    @property
    def is_named(self) -> bool:
        return all(member.name is not None for member in self.members)


class CastType(Enum):
    # When the compiler creates a cast expression for references.
    FORCED = 0
    # When an explicit cast occurs using 'cast(*, *)'.
    EXPLICIT = auto()
    # When unpacking occurs (e.g., 'let (x: T) = foo();').
    UNPACKING = auto()
    # When a variable is initialized (e.g., 'tempvar x: T = 5;').
    ASSIGN = auto()


@dataclasses.dataclass
class ExprIdentifier(AstNode):
    name: str

    def get_children(self) -> Sequence[Optional[AstNode]]:
        return []
