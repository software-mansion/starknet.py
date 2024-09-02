# pylint: disable=import-outside-toplevel, pointless-string-statement, unbalanced-tuple-unpacking
import json

from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract


def test_short_strings():
    # docs-shortstring: start
    from starknet_py.cairo.felt import decode_shortstring, encode_shortstring

    # Convert a string literal to its felt value
    encoded = encode_shortstring("myshortstring")
    assert encoded == 0x6D7973686F7274737472696E67

    # Decode a felt into a string
    decoded = decode_shortstring(encoded)
    assert decoded == "myshortstring"
    # docs-shortstring: end


def test_abi_parsing():
    raw_abi_string = json.loads(
        load_contract(contract_name="TestContract", version=ContractVersion.V2)[
            "sierra"
        ]
    )["abi"]
    # docs-serializer: start
    from starknet_py.abi.v2 import AbiParser

    """
    #[external(v0)]
    fn test(ref self: ContractState, ref arg: felt252, arg1: felt252, arg2: felt252) -> felt252 {
        let mut x = self.my_storage_var.read();
        x += 1;
        self.my_storage_var.write(x);
        x + internal_func()
    }
    """

    abi = AbiParser(raw_abi_string).parse()

    from starknet_py.serialization.factory import serializer_for_function_v1

    # You can create serializer for function inputs/outputs by passing Abi.Function object to serializer_for_function
    function_serializer = serializer_for_function_v1(abi.functions["test"])

    # You can call function serializer like you would a normal function
    assert [111, 222, 333] == function_serializer.serialize(arg=111, arg1=222, arg2=333)
    assert [111, 222, 333] == function_serializer.serialize(111, 222, 333)
    assert [111, 222, 333] == function_serializer.serialize(111, 222, arg2=333)

    # You can use deserialized result from function serializer like a tuple
    result = function_serializer.deserialize([1])
    (success,) = result
    assert success == 1
    # docs-serializer: end

    raw_abi_string = json.loads(
        load_contract(contract_name="ERC20", version=ContractVersion.V2)["sierra"]
    )["abi"]
    abi = AbiParser(raw_abi_string).parse()

    # docs-event: start
    from starknet_py.serialization import serializer_for_event

    """
    #[event]
    #[derive(Drop, starknet::Event)]
    struct Approval {
        owner: ContractAddress,
        spender: ContractAddress,
        value: u256,
    }
    """

    # You can create serializer for events by passing Abi.Event object to serializer_for_event
    event_serializer = serializer_for_event(
        abi.events["contracts_v2::erc20::ERC20::Approval"]
    )

    assert [1, 2, 3, 4] == event_serializer.serialize(
        {"owner": 1, "spender": 2, "value": 3 + 4 * 2**128}
    )
    assert {
        "owner": 1,
        "spender": 2,
        "value": 3 + 4 * 2**128,
    } == event_serializer.deserialize([1, 2, 3, 4]).as_dict()
    # docs-event: end
