import starknet_py.tests.e2e.fixtures.abi_v1_structures as fixtures
from starknet_py.abi.v1.parser import AbiParser


def test_parsing_types_abi():
    abi = AbiParser(
        [
            fixtures.foo_external_dict,
            fixtures.foo_event_dict,
            fixtures.foo_view_dict,
            fixtures.my_enum_dict,
            fixtures.my_struct_dict,
        ]
    ).parse()

    assert abi.defined_structures == {
        "test::MyStruct::<core::integer::u256>": fixtures.my_struct,
    }
    assert abi.defined_enums == {
        "test::MyEnum::<core::integer::u128>": fixtures.my_enum,
    }
    assert abi.events == {
        "foo_event": fixtures.foo_event,
    }
    assert abi.functions == {
        "foo_external": fixtures.foo_external,
        "foo_view": fixtures.foo_view,
    }
