from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from .data_transformer import DataTransformer


def transformer_for_function(inputs, structs=None):
    structs = structs or []
    fun_abi = {
        "inputs": inputs,
        "name": "test_fun",
        "outputs": [{"name": "value", "type": "felt"}],
        "stateMutability": "view",
        "type": "function",
    }
    full_abi = [fun_abi, *structs]
    return DataTransformer(
        abi=fun_abi, identifier_manager=identifier_manager_from_abi(full_abi)
    )


def test_array():
    transformer = transformer_for_function(
        [{"name": "array_len", "type": "felt"}, {"name": "array", "type": "felt*"}]
    )

    result = transformer([1, 2, 3])

    assert result == [3, 1, 2, 3]


def test_empty_array():
    transformer = transformer_for_function(
        [{"name": "array_len", "type": "felt"}, {"name": "array", "type": "felt*"}]
    )

    result = transformer([])

    assert result == [0]


def test_felt():
    transformer = transformer_for_function([{"name": "value", "type": "felt"}])

    result = transformer(1234)

    assert result == [1234]


def test_struct():
    transformer = transformer_for_function(
        [{"name": "value", "type": "SimpleStruct"}],
        [
            {
                "members": [
                    {"name": "first", "offset": 0, "type": "felt"},
                    {"name": "second", "offset": 1, "type": "(felt, felt, felt)"},
                ],
                "name": "SimpleStruct",
                "size": 4,
                "type": "struct",
            }
        ],
    )

    result = transformer({"first": 1, "second": (2, 3, 4)})

    assert result == [1, 2, 3, 4]


def test_nested_struct():
    transformer = transformer_for_function(
        [{"name": "value", "type": "StructWithStruct"}],
        [
            {
                "members": [
                    {"name": "first", "offset": 0, "type": "NestedStruct"},
                    {"name": "second", "offset": 1, "type": "(felt, felt, felt)"},
                    {"name": "third", "offset": 2, "type": "DeeplyNestedStruct"},
                ],
                "name": "StructWithStruct",
                "size": 4,
                "type": "struct",
            },
            {
                "members": [
                    {
                        "name": "deeply_nested",
                        "offset": 0,
                        "type": "DeeplyNestedStruct",
                    },
                ],
                "name": "NestedStruct",
                "size": 1,
                "type": "struct",
            },
            {
                "members": [
                    {"name": "nested", "offset": 0, "type": "felt"},
                ],
                "name": "DeeplyNestedStruct",
                "size": 1,
                "type": "struct",
            },
        ],
    )

    result = transformer(
        {
            "first": {"deeply_nested": {"nested": 1}},
            "second": (2, 3, 4),
            "third": {"nested": 5},
        }
    )

    assert result == [1, 2, 3, 4, 5]


def test_multiple_values():
    transformer = transformer_for_function(
        [
            {"name": "first", "type": "felt"},
            {"name": "second_len", "type": "felt"},
            {"name": "second", "type": "felt*"},
            {"name": "third", "type": "(felt, felt)"},
        ],
    )

    result = transformer(1, second=[2, 3, 4, 5], third=(6, 7))

    assert result == [1, 4, 2, 3, 4, 5, 6, 7]
