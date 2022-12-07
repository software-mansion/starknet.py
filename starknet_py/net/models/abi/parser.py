from __future__ import annotations

from collections import OrderedDict, defaultdict
from typing import Dict, List, TypeVar, Optional, cast, DefaultDict

from marshmallow import EXCLUDE

from starknet_py.cairo.type_parser import TypeParser
from starknet_py.cairo.data_types import StructType, CairoType
from starknet_py.net.models.abi.model import Abi
from starknet_py.net.models.abi.schemas import ContractAbiEntrySchema
from starknet_py.net.models.abi.shape import (
    FunctionDict,
    TypedMemberDict,
    EventDict,
    STRUCT_ENTRY,
    FUNCTION_ENTRY,
    EVENT_ENTRY,
    CONSTRUCTOR_ENTRY,
    L1_HANDLER_ENTRY,
    StructMemberDict,
    AbiDictList,
)


class AbiParsingError(ValueError):
    pass


Entry = TypeVar("Entry", bound=Dict)


class AbiParser:
    # Entries from ABI grouped by entry type
    _grouped: DefaultDict[str, AbiDictList]
    # lazy init property
    _type_parser: Optional[TypeParser] = None

    def __init__(self, abi_list: AbiDictList):
        abi = [
            ContractAbiEntrySchema().load(entry, unknown=EXCLUDE) for entry in abi_list
        ]
        grouped = defaultdict(list)
        for entry in abi:
            grouped[entry["type"]].append(entry)

        self._grouped = grouped

    def parse(self) -> Abi:
        structures = self._parse_structures()
        functions_dict = AbiParser._group_by_entry_name(
            self._grouped[FUNCTION_ENTRY], "defined functions"
        )
        events_dict = AbiParser._group_by_entry_name(
            self._grouped[EVENT_ENTRY], "defined events"
        )
        constructors = self._grouped[CONSTRUCTOR_ENTRY]
        l1_handlers = self._grouped[L1_HANDLER_ENTRY]

        if len(l1_handlers) > 1:
            raise AbiParsingError("L1 handler in ABI must be defined at most once")

        if len(constructors) > 1:
            raise AbiParsingError("Constructor in ABI must be defined at most once")

        return Abi(
            defined_structures=structures,
            constructor=(
                self._parse_function(constructors[0]) if constructors else None
            ),
            l1_handler=(self._parse_function(l1_handlers[0]) if l1_handlers else None),
            functions={
                name: self._parse_function(entry)
                for name, entry in functions_dict.items()
            },
            events={
                name: self._parse_event(entry) for name, entry in events_dict.items()
            },
        )

    @property
    def type_parser(self) -> TypeParser:
        if self._type_parser:
            return self._type_parser

        raise RuntimeError("Tried to get type_parser before it was set")

    def _parse_structures(self) -> Dict[str, StructType]:
        structs_dict = AbiParser._group_by_entry_name(
            self._grouped[STRUCT_ENTRY], "defined structures"
        )

        # Contains sorted members of the struct
        struct_members: Dict[str, List[StructMemberDict]] = {}
        structs: Dict[str, StructType] = {}

        # Example problem (with a simplified json structure):
        # [{name: User, fields: {id: Uint256}}, {name: "Uint256", ...}]
        # User refers to Uint256 even though it is not known yet (will be parsed next).
        # This is why it is important to create the structure types first. This way other types can already refer to
        # them when parsing types, even thought their fields are not filled yet.
        # At the end we will mutate those structures to contain the right fields. An alternative would be to use
        # topological sorting with an additional "unresolved type", so this flow is much easier.
        for name, struct in structs_dict.items():
            structs[name] = StructType(name, OrderedDict())
            struct_members[name] = sorted(
                struct["members"], key=lambda member: member["offset"]
            )

        # Now parse the types of members and save them.
        self._type_parser = TypeParser(structs)
        for name, struct in structs.items():
            members = self._parse_members(
                f"members of structure '{name}'",
                # pyright can't handle list of StructMemberDict here, even though TypedMemberDict
                # is parent of StructMemberDict
                cast(List[TypedMemberDict], struct_members[name]),
            )
            struct.types.update(members)

        # All types have their members assigned now
        return structs

    def _parse_function(self, function: FunctionDict) -> Abi.Function:
        return Abi.Function(
            name=function["name"],
            inputs=self._parse_members(function["name"], function["inputs"]),
            outputs=self._parse_members(function["name"], function["outputs"]),
        )

    def _parse_event(self, event: EventDict) -> Abi.Event:
        return Abi.Event(
            name=event["name"],
            data=self._parse_members(event["name"], event["data"]),
        )

    def _parse_members(
        self, entity_name: str, params: List[TypedMemberDict]
    ) -> OrderedDict[str, CairoType]:
        # Without cast it complains that
        # 'Type "TypedMemberDict" cannot be assigned to type "T@_group_by_name"'
        members = AbiParser._group_by_entry_name(cast(List[Dict], params), entity_name)
        return OrderedDict(
            (name, self.type_parser.parse_inline_type(param["type"]))
            for name, param in members.items()
        )

    @staticmethod
    def _group_by_entry_name(
        dicts: List[Entry], entity_name: str
    ) -> OrderedDict[str, Entry]:
        grouped = OrderedDict()
        for entry in dicts:
            name = entry["name"]
            if name in grouped:
                raise AbiParsingError(
                    f"Name '{name}' was used more than once in {entity_name}"
                )
            grouped[name] = entry
        return grouped
