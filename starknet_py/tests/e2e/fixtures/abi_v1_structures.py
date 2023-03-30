# data from cairo repository: crates/cairo-lang-starknet/src/abi_test.rs
from collections import OrderedDict

from starknet_py.abi.v1.model import Abi
from starknet_py.cairo.data_types import FeltType, StructType

my_struct_dict = {
    "type": "struct",
    "name": "test::MyStruct::<core::integer::u256>",
    "members": [
        {"name": "a", "type": "core::integer::u256"},
        {"name": "b", "type": "core::felt252"},
    ],
}
my_struct = StructType(
    name="test::MyStruct::<core::integer::u256>",
    types=OrderedDict(a=FeltType(), b=FeltType()),
)

my_enum_dict = {
    "type": "enum",
    "name": "test::MyEnum::<core::integer::u128>",
    "variants": [
        {"name": "a", "type": "core::integer::u256"},
        {"name": "b", "type": "test::MyStruct::<core::integer::u128>"},
    ],
}
my_enum = StructType(
    name="test::MyEnum::<core::integer::u128>",
    types=OrderedDict(a=FeltType(), b=my_struct),
)

foo_event_dict = {
    "type": "event",
    "name": "foo_event",
    "inputs": [
        {"name": "a", "type": "core::felt252"},
        {"name": "b", "type": "core::integer::u128"},
    ],
}
foo_event = Abi.Event(name="foo_event", inputs=OrderedDict(a=FeltType(), b=FeltType()))

foo_external_dict = {
    "type": "function",
    "name": "foo_external",
    "inputs": [
        {"name": "a", "type": "core::felt252"},
        {"name": "b", "type": "core::integer::u128"},
    ],
    "outputs": [{"type": "test::MyStruct::<core::integer::u256>"}],
    "state_mutability": "external",
}
foo_external = Abi.Function(
    name="foo_external",
    inputs=OrderedDict(a=FeltType(), b=FeltType()),
    outputs=[my_struct],
)

foo_view_dict = {
    "type": "function",
    "name": "foo_view",
    "inputs": [
        {"name": "a", "type": "core::felt252"},
        {"name": "b", "type": "core::integer::u128"},
    ],
    "outputs": [{"type": "test::MyEnum::<core::integer::u128>"}],
    "state_mutability": "view",
}
foo_view = Abi.Function(
    name="foo_view", inputs=OrderedDict(a=FeltType(), b=FeltType()), outputs=[my_enum]
)
