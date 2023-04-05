from __future__ import annotations

import dataclasses
import json
from collections import OrderedDict, defaultdict
from typing import DefaultDict, Dict, List, Optional, cast

from marshmallow import EXCLUDE

from starknet_py.abi.v1.model import Abi
from starknet_py.abi.v1.schemas import ContractAbiEntrySchema
from starknet_py.abi.v1.shape import (
    ENUM_ENTRY,
    EVENT_ENTRY,
    FUNCTION_ENTRY,
    STRUCT_ENTRY,
    EventDict,
    FunctionDict,
    TypedParameterDict,
)
from starknet_py.cairo.data_types import CairoType, StructType
from starknet_py.cairo.v1.type_parser import TypeParser


class AbiParsingError(ValueError):
    """
    Error raised when something wrong goes during abi parsing.
    """


class AbiParser:
    """
    Utility class for parsing abi into a dataclass.
    """

    # Entries from ABI grouped by entry type
    _grouped: DefaultDict[str, List[Dict]]
    # lazy init property
    _type_parser: Optional[TypeParser] = None

    def __init__(self, abi_list: List[Dict]):
        """
        Abi parser constructor. Ensures that abi satisfies the abi schema.

        :param abi_list: Contract's ABI as a list of dictionaries.
        """
        abi = [
            ContractAbiEntrySchema().load(entry, unknown=EXCLUDE) for entry in abi_list
        ]
        grouped = defaultdict(list)
        for entry in abi:
            grouped[entry["type"]].append(entry)

        self._grouped = grouped

    def parse(self) -> Abi:
        """
        Parse abi provided to constructor and return it as a dataclass. Ensures that there are no cycles in the abi.

        :raises: AbiParsingError: on any parsing error.
        :return: Abi dataclass.
        """
        structures = self._parse_structures()
        functions_dict = cast(
            Dict[str, FunctionDict],
            AbiParser._group_by_entry_name(
                self._grouped[FUNCTION_ENTRY], "defined functions"
            ),
        )
        events_dict = cast(
            Dict[str, EventDict],
            AbiParser._group_by_entry_name(
                self._grouped[EVENT_ENTRY], "defined events"
            ),
        )

        return Abi(
            defined_structures=structures,
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

        raise RuntimeError("Tried to get type_parser before it was set.")

    def _parse_structures(self) -> Dict[str, StructType]:
        structs_dict = AbiParser._group_by_entry_name(
            self._grouped[STRUCT_ENTRY], "defined structures"
        )
        structs_dict.update(
            AbiParser._group_by_entry_name(
                self._grouped[ENUM_ENTRY], "defined structures"
            )
        )

        # Contains sorted members of the struct
        struct_members: Dict[str, List[TypedParameterDict]] = {}
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
            if "members" in struct.keys():
                struct_members[name] = struct["members"]
            else:
                struct_members[name] = struct["variants"]

        # Now parse the types of members and save them.
        self._type_parser = TypeParser(structs)
        for name, struct in structs.items():
            members = self._parse_members(
                cast(List[TypedParameterDict], struct_members[name]),
                f"members of structure '{name}'",
            )
            struct.types.update(members)

        # All types have their members assigned now

        self._check_for_cycles(structs)

        return structs

    @staticmethod
    def _check_for_cycles(structs: Dict[str, StructType]):
        # We want to avoid creating our own cycle checker as it would make it more complex. json module has a built-in
        # checker for cycles.
        try:
            _to_json(structs)
        except ValueError as err:
            raise AbiParsingError(err) from ValueError

    def _parse_function(self, function: FunctionDict) -> Abi.Function:
        return Abi.Function(
            name=function["name"],
            inputs=self._parse_members(function["inputs"], function["name"]),
            outputs=list(
                self.type_parser.parse_inline_type(param["type"])
                for param in function["outputs"]
            ),
        )

    def _parse_event(self, event: EventDict) -> Abi.Event:
        return Abi.Event(
            name=event["name"],
            inputs=self._parse_members(event["inputs"], event["name"]),
        )

    def _parse_members(
        self, params: List[TypedParameterDict], entity_name: str
    ) -> OrderedDict[str, CairoType]:
        # Without cast, it complains that 'Type "TypedParameterDict" cannot be assigned to type "T@_group_by_name"'
        members = AbiParser._group_by_entry_name(cast(List[Dict], params), entity_name)
        return OrderedDict(
            (name, self.type_parser.parse_inline_type(param["type"]))
            for name, param in members.items()
        )

    @staticmethod
    def _group_by_entry_name(
        dicts: List[Dict], entity_name: str
    ) -> OrderedDict[str, Dict]:
        grouped = OrderedDict()
        for entry in dicts:
            name = entry["name"]
            if name in grouped:
                raise AbiParsingError(
                    f"Name '{name}' was used more than once in {entity_name}."
                )
            grouped[name] = entry
        return grouped


def _to_json(value):
    class DataclassSupportingEncoder(json.JSONEncoder):
        def default(self, o):
            # Dataclasses are not supported by json. Additionally, dataclasses.asdict() works recursively and doesn't
            # check for cycles, so we need to flatten dataclasses (by ONE LEVEL) ourselves.
            if dataclasses.is_dataclass(o):
                return tuple(getattr(o, field.name) for field in dataclasses.fields(o))
            return super().default(o)

    return json.dumps(value, cls=DataclassSupportingEncoder)
