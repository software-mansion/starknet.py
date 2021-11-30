import pytest
from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from .data_transformer import DataTransformer


def transformer_for_function(inputs=None, outputs=None, structs=None):
    structs = structs or []
    inputs = inputs or []
    outputs = outputs or []
    fun_abi = {
        "inputs": inputs,
        "name": "test_fun",
        "outputs": outputs,
        "stateMutability": "view",
        "type": "function",
    }
    full_abi = [fun_abi, *structs]
    return DataTransformer(
        abi=fun_abi, identifier_manager=identifier_manager_from_abi(full_abi)
    )


@pytest.mark.parametrize(
    "value, cairo_value",
    [
        ([1, 2, 3], [3, 1, 2, 3]),
        ([], [0]),
        ([213], [1, 213]),
        ([1, 1, 1, 1, 1, 1], [6, 1, 1, 1, 1, 1, 1]),
    ],
)
def test_array(value, cairo_value):
    abi = [
        {"name": "array_len", "type": "felt"},
        {"name": "array", "type": "felt*"},
    ]

    from_python = transformer_for_function(inputs=abi)(value)
    to_python = transformer_for_function(outputs=abi).to_python(cairo_value)

    assert from_python == cairo_value
    assert to_python == {"array": value, "array_len": len(value)}


@pytest.mark.parametrize(
    "value, cairo_value",
    [
        ((1, 2, 3), [1, 2, 3]),
        ((1,), [1]),
        ((213, 2), [213, 2]),
        ((1, 1, 1, 1, 1, 1), [1, 1, 1, 1, 1, 1]),
    ],
)
def test_tuple(value, cairo_value):
    print(value)
    cairo_type_name = "felt," * len(value)
    abi = [
        {"name": "value", "type": f"({cairo_type_name})"},
    ]

    from_python = transformer_for_function(inputs=abi)(value)
    to_python = transformer_for_function(outputs=abi).to_python(cairo_value)

    assert from_python == cairo_value
    assert to_python == {"value": value}


@pytest.mark.parametrize(
    "value, cairo_value",
    [(0, [0]), (1, [1]), (-1, [-1]), (322132123, [322132123])],
)
def test_felt(value, cairo_value):
    abi = [{"name": "value", "type": "felt"}]

    from_python = transformer_for_function(inputs=abi)(value)
    to_python = transformer_for_function(outputs=abi).to_python(cairo_value)

    assert from_python == cairo_value
    assert to_python == {"value": value}


@pytest.mark.parametrize(
    "value, cairo_value",
    [({"first": 1, "second": (2, 3, 4)}, [1, 2, 3, 4])],
)
def test_struct(value, cairo_value):
    abi = [{"name": "value", "type": "SimpleStruct"}]
    structs = [
        {
            "members": [
                {"name": "first", "offset": 0, "type": "felt"},
                {"name": "second", "offset": 1, "type": "(felt, felt, felt)"},
            ],
            "name": "SimpleStruct",
            "size": 4,
            "type": "struct",
        }
    ]

    from_python = transformer_for_function(inputs=abi, structs=structs)(value)
    to_python = transformer_for_function(outputs=abi, structs=structs).to_python(
        cairo_value
    )

    assert from_python == cairo_value
    assert to_python == {"value": value}


def test_nested_struct():
    transformer = transformer_for_function(
        inputs=[{"name": "value", "type": "StructWithStruct"}],
        structs=[
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
        inputs=[
            {"name": "first", "type": "felt"},
            {"name": "second_len", "type": "felt"},
            {"name": "second", "type": "felt*"},
            {"name": "third", "type": "(felt, felt)"},
        ],
    )

    result = transformer(1, second=[2, 3, 4, 5], third=(6, 7))

    assert result == [1, 4, 2, 3, 4, 5, 6, 7]
