from __future__ import annotations

from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Iterable, TypeVar, Optional, Union, cast, Sequence

from marshmallow import EXCLUDE

from starknet_py.cairo.type_parser import TypeParser
from starknet_py.cairo.data_types import StructType, CairoType
from starknet_py.net.models.abi.schemas import ContractAbiEntrySchema
from starknet_py.net.models.abi.shape import (
    StructDict,
    FunctionDict,
    TypedMemberDict,
    EventDict,
    STRUCT_ENTRY,
    FUNCTION_ENTRY,
    EVENT_ENTRY,
    CONSTRUCTOR_ENTRY,
    L1_HANDLER_ENTRY,
    StructMemberDict,
)


class AbiDecodingError(ValueError):
    pass


T = TypeVar("T", bound=Dict)


@dataclass
class AbiDefinition:
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

    @staticmethod
    def from_list(abi_list: List[Dict]) -> AbiDefinition:
        abi = [
            ContractAbiEntrySchema().load(entry, unknown=EXCLUDE) for entry in abi_list
        ]

        grouped = defaultdict(list)
        for entry in abi:
            grouped[entry["type"]].append(entry)

        structs_dict = AbiDefinition._group_by_name(
            "defined structures", grouped[STRUCT_ENTRY]
        )
        functions_dict = AbiDefinition._group_by_name(
            "defined functions", grouped[FUNCTION_ENTRY]
        )
        events_dict = AbiDefinition._group_by_name(
            "defined events", grouped[EVENT_ENTRY]
        )
        constructors = grouped[CONSTRUCTOR_ENTRY]
        l1_handlers = grouped[L1_HANDLER_ENTRY]

        if len(l1_handlers) > 1:
            raise AbiDecodingError("L1 handler in ABI must be defined at most once")

        if len(constructors) > 1:
            raise AbiDecodingError("Constructor in ABI must be defined at most once")

        structures = AbiDefinition._parse_abi_structs(structs_dict)
        parser = TypeParser(structures)

        return AbiDefinition(
            defined_structures=structures,
            constructor=AbiDefinition._parse_abi_function(constructors[0], parser)
            if constructors
            else None,
            l1_handler=AbiDefinition._parse_abi_function(l1_handlers[0], parser)
            if l1_handlers
            else None,
            functions={
                name: AbiDefinition._parse_abi_function(entry, parser)
                for name, entry in functions_dict.items()
            },
            events={
                name: AbiDefinition._parse_event(entry, parser)
                for name, entry in events_dict.items()
            },
        )

    @staticmethod
    def _parse_abi_structs(
        structs_dict: Dict[str, StructDict]
    ) -> Dict[str, StructType]:
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
            struct_members[name] = sorted(struct["members"], key=lambda m: m["offset"])

        # Now parse the types of members and save them.
        type_parser = TypeParser(structs)
        for name, struct in structs.items():
            members = AbiDefinition._parse_members(
                f"members of structure '{name}'",
                # pyright can't handle list of StructMemberDict here, even though TypedMemberDict
                # is parent of StructMemberDict
                cast(List[TypedMemberDict], struct_members[name]),
                type_parser,
            )
            struct.types.update(members)

        # All types have their members assigned now
        return structs

    @staticmethod
    def _parse_abi_function(
        function: FunctionDict, type_parser: TypeParser
    ) -> AbiDefinition.Function:
        return AbiDefinition.Function(
            name=function["name"],
            inputs=AbiDefinition._parse_members(
                function["name"], function["inputs"], type_parser
            ),
            outputs=AbiDefinition._parse_members(
                function["name"], function["outputs"], type_parser
            ),
        )

    @staticmethod
    def _parse_event(event: EventDict, type_parser: TypeParser) -> AbiDefinition.Event:
        return AbiDefinition.Event(
            name=event["name"],
            data=AbiDefinition._parse_members(
                event["name"], event["data"], type_parser
            ),
        )

    @staticmethod
    def _parse_members(
        entity_name: str, params: List[TypedMemberDict], parser: TypeParser
    ) -> OrderedDict[str, CairoType]:
        # Without cast it complains that
        # 'Type "TypedMemberDict" cannot be assigned to type "T@_group_by_name"'
        members = AbiDefinition._group_by_name(entity_name, cast(List[Dict], params))
        return OrderedDict(
            (name, parser.parse_inline_type(param["type"]))
            for name, param in members.items()
        )

    @staticmethod
    def _group_by_name(entity_name: str, dicts: List[T]) -> OrderedDict[str, T]:
        grouped = OrderedDict()
        for entry in dicts:
            name = entry["name"]
            if name in grouped:
                raise AbiDecodingError(
                    f"Name '{name}' was used more than once in {entity_name}"
                )
            grouped[name] = entry
        return grouped
