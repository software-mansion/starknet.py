# pylint: disable=import-outside-toplevel, pointless-string-statement
import json

from starknet_py.tests.e2e.fixtures.misc import read_contract


def test_short_strings():
    # docs-shortstring: start
    from starknet_py.cairo.felt import decode_shortstring, encode_shortstring

    # Convert a string literal to its felt value
    encoded = encode_shortstring("myshortstring")
    assert encoded == 0x6D7973686F7274737472696E67

    # Decode a felt into a string
    # Note that decoded value always has 31 characters in length.
    # Extra `\x00` characters can be stripped to get only the encoded value.
    decoded = decode_shortstring(encoded).lstrip("\x00")
    assert decoded == "myshortstring"
    # docs-shortstring: end


def test_abi_parsing():
    raw_abi_string = read_contract("erc20_abi.json")
    # docs-serializer: start
    from starknet_py.abi import AbiParser

    """
    @external
    func transferFrom{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
        sender: felt, recipient: felt, amount: felt
    ) -> (success: felt) {
        alloc_locals;
        local success: felt = 1;
        return (success,);
    }
    """

    erc20_abi = json.loads(raw_abi_string)
    abi = AbiParser(erc20_abi).parse()

    from starknet_py.serialization import serializer_for_function

    # You can create serializer for function inputs/outputs by passing Abi.Function object to serializer_for_function
    function_serializer = serializer_for_function(abi.functions["transferFrom"])

    # You can call function serializer like you would a normal function
    assert [111, 222, 333] == function_serializer.serialize(
        sender=111, recipient=222, amount=333
    )
    assert [111, 222, 333] == function_serializer.serialize(111, 222, 333)
    assert [111, 222, 333] == function_serializer.serialize(111, 222, amount=333)

    # You can use deserialized result from function serializer like a tuple, but it also has named properties
    result = function_serializer.deserialize([1])
    assert 1 == result[0]
    assert 1 == result.success
    assert {"success": 1} == result.as_dict()
    (success,) = result
    assert 1 == success
    # docs-serializer: end

    # docs-event: start
    from starknet_py.serialization import serializer_for_event

    """
    @event
    func Transfer(from_: felt, to: felt, value: Uint256) {
    }
    """

    # You can create serializer for events by passing Abi.Event object to serializer_for_event
    event_serializer = serializer_for_event(abi.events["Transfer"])
    assert [1, 2, 3, 4] == event_serializer.serialize(
        {"from_": 1, "to": 2, "value": 3 + 4 * 2**128}
    )
    assert {
        "from_": 1,
        "to": 2,
        "value": 3 + 4 * 2**128,
    } == event_serializer.deserialize([1, 2, 3, 4]).as_dict()
    # docs-event: end
