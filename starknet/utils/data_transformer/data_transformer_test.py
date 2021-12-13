import pytest
from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet.utils.types import UInt256
from starknet.utils.data_transformer.data_transformer import DataTransformer


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

    from_python, _args = transformer_for_function(inputs=abi).from_python(value)
    to_python = transformer_for_function(outputs=abi).to_python(cairo_value)

    assert from_python == cairo_value
    assert to_python == (value,)


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
    cairo_type_name = "felt," * len(value)
    abi = [
        {"name": "value", "type": f"({cairo_type_name})"},
    ]

    from_python, _args = transformer_for_function(inputs=abi).from_python(value)
    to_python = transformer_for_function(outputs=abi).to_python(cairo_value)

    assert from_python == cairo_value
    assert to_python == (value,)


@pytest.mark.parametrize(
    "value, cairo_value",
    [(0, [0]), (1, [1]), (-1, [-1]), (322132123, [322132123])],
)
def test_felt(value, cairo_value):
    abi = [{"name": "value", "type": "felt"}]

    from_python, _args = transformer_for_function(inputs=abi).from_python(value)
    to_python = transformer_for_function(outputs=abi).to_python(cairo_value)

    assert from_python == cairo_value
    assert to_python == (value,)


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

    from_python, _args = transformer_for_function(
        inputs=abi, structs=structs
    ).from_python(value)
    to_python = transformer_for_function(outputs=abi, structs=structs).to_python(
        cairo_value
    )

    assert from_python == cairo_value
    assert to_python == (value,)


@pytest.mark.parametrize(
    "value, cairo_value",
    [
        (123, [123, 0]),  # (python int, [low, high])
        (12345, [12345, 0]),
        (((1 << 128) - 1), [((1 << 128) - 1), 0]),  # 128 low bits filled
        (
            ((1 << 256) - 1) ^ ((1 << 128) - 1),
            [0, ((1 << 128) - 1)],
        ),  # 128 high bits filled
        (
            (1 << 256) - 1,  # Max - all 1 (256 bits)
            [
                ((1 << 256) - 1) >> 128,  # Low, all 1 (128 bits)
                ((1 << 256) - 1) >> 128,  # High, all 1 (128 bits)
            ],
        ),
        (0, [0, 0]),
    ],
)
def test_uint256(value: int, cairo_value):
    uint = UInt256(value)
    abi = [{"name": "value", "type": "Uint256"}]
    structs = [
        {
            "members": [
                {"name": "low", "offset": 0, "type": "felt"},
                {"name": "high", "offset": 1, "type": "felt"},
            ],
            "name": "Uint256",
            "size": 2,
            "type": "struct",
        }
    ]

    from_python, _ = transformer_for_function(inputs=abi, structs=structs).from_python(
        uint
    )
    to_python = transformer_for_function(outputs=abi, structs=structs).to_python(
        cairo_value
    )

    assert from_python == cairo_value
    assert to_python == (uint,)


@pytest.mark.parametrize(
    "invalid_value",
    [-1, -2, -3, -5, -(2 << 128), -(2 << 256)],
)
def test_invalid_uint256(invalid_value: int):
    with pytest.raises(ValueError) as v_err:
        UInt256(invalid_value)
        assert "in range [0;2^256)" in str(v_err.value)


def test_nested_struct():
    structs = [
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
    ]
    abi = [{"name": "value", "type": "StructWithStruct"}]
    value = {
        "first": {"deeply_nested": {"nested": 1}},
        "second": (2, 3, 4),
        "third": {"nested": 5},
    }
    cairo_value = [1, 2, 3, 4, 5]

    from_python, _args = transformer_for_function(
        inputs=abi, structs=structs
    ).from_python(value)
    to_python = transformer_for_function(outputs=abi, structs=structs).to_python(
        cairo_value
    )

    assert from_python == cairo_value
    assert to_python == (value,)


def test_multiple_values():
    abi = [
        {"name": "first", "type": "felt"},
        {"name": "second_len", "type": "felt"},
        {"name": "second", "type": "felt*"},
        {"name": "third", "type": "(felt, felt)"},
    ]
    values = [123, [10, 20], (-11, -12)]
    cairo_values = [123, 2, 10, 20, -11, -12]

    calldata, args = transformer_for_function(inputs=abi).from_python(*values)
    to_python = transformer_for_function(outputs=abi).to_python(cairo_values)

    assert calldata == cairo_values
    assert args == {"first": [123], "second": [2, 10, 20], "third": [-11, -12]}
    assert to_python == (123, [10, 20], (-11, -12))
    assert to_python.as_dict() == {
        "first": 123,
        "second": [10, 20],
        "third": (-11, -12),
    }


def test_not_enough_felts():
    abi = [{"name": "first", "type": "felt"}, {"name": "second", "type": "felt"}]

    with pytest.raises(ValueError) as excinfo:
        transformer_for_function(outputs=abi).to_python([1])

    assert "second expected 1 values" in str(excinfo.value)


def test_invalid_tuple_length():
    abi = [{"name": "value", "type": "(felt, felt, felt)"}]

    with pytest.raises(ValueError) as excinfo:
        transformer_for_function(inputs=abi).from_python((1, 2))

    assert "2 != 3" in str(excinfo.value)


def test_missing_struct_key():
    abi = [{"name": "value", "type": "SimpleStruct"}]
    structs = [
        {
            "members": [
                {"name": "first", "offset": 0, "type": "felt"},
                {"name": "second", "offset": 1, "type": "felt"},
            ],
            "name": "SimpleStruct",
            "size": 4,
            "type": "struct",
        }
    ]

    with pytest.raises(ValueError) as excinfo:
        transformer_for_function(inputs=abi, structs=structs).from_python({"first": 1})

    assert "value[second] not provided" in str(excinfo.value)


@pytest.mark.parametrize(
    "cairo_type, value",
    [
        ("felt", []),
        ("(felt, felt)", 1),
        ("SimpleStruct", 1),
    ],
)
def test_wrong_types(cairo_type, value):
    abi = [{"name": "value", "type": cairo_type}]
    structs = [
        {
            "members": [
                {"name": "first", "offset": 0, "type": "felt"},
                {"name": "second", "offset": 1, "type": "felt"},
            ],
            "name": "SimpleStruct",
            "size": 4,
            "type": "struct",
        }
    ]

    with pytest.raises(TypeError):
        transformer_for_function(inputs=abi, structs=structs).from_python(value)


def test_too_many_positional_args():
    abi = [{"name": "value", "type": "felt"}]

    with pytest.raises(TypeError) as excinfo:
        transformer_for_function(inputs=abi).from_python(1, 2)

    assert "2 positional arguments" in str(excinfo.value)


def test_arg_provided_twice():
    abi = [{"name": "value", "type": "felt"}]

    with pytest.raises(TypeError) as excinfo:
        transformer_for_function(inputs=abi).from_python(1, value=2)

    assert "positional and named argument provided" in str(excinfo.value)


def test_missing_arg():
    abi = [{"name": "first", "type": "felt"}, {"name": "second", "type": "felt"}]

    with pytest.raises(TypeError) as excinfo:
        transformer_for_function(inputs=abi).from_python(1)

    assert "second not provided" in str(excinfo.value)
