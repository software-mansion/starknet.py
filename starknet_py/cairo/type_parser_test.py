from collections import OrderedDict

import pytest

from starknet_py.cairo.data_types import (
    FeltType,
    NamedTupleType,
    TupleType,
    ArrayType,
    StructType,
)
from starknet_py.cairo.type_parser import TypeParser, UnknownTypeError


@pytest.mark.parametrize(
    "type_string, expected",
    [
        ("felt", FeltType()),
        ("felt*", ArrayType(FeltType())),
        ("(felt, felt, felt, felt)", TupleType([FeltType()] * 4)),
        (
            "(low: felt, high: felt)",
            NamedTupleType(OrderedDict(low=FeltType(), high=FeltType())),
        ),
        ("()", TupleType([])),
        (
            "(a: felt, b: (felt, (felt*, felt)))",
            NamedTupleType(
                OrderedDict(
                    a=FeltType(),
                    b=TupleType(
                        [
                            FeltType(),
                            TupleType(
                                [
                                    ArrayType(FeltType()),
                                    FeltType(),
                                ]
                            ),
                        ]
                    ),
                )
            ),
        ),
    ],
)
def test_parse_without_defined_types(type_string, expected):
    parsed = TypeParser({}).parse_inline_type(type_string)
    assert parsed == expected


uint256_type = StructType("Uint256", OrderedDict(low=FeltType(), high=FeltType()))
wrapped_felt_type = StructType("WrappedFelt", OrderedDict(value=FeltType()))


@pytest.mark.parametrize(
    "type_string, expected",
    [
        ("Uint256", uint256_type),
        ("Uint256*", ArrayType(uint256_type)),
        ("(Uint256, WrappedFelt)", TupleType([uint256_type, wrapped_felt_type])),
        (
            "(a: Uint256, b: (WrappedFelt, (felt*, WrappedFelt*)))",
            NamedTupleType(
                OrderedDict(
                    a=uint256_type,
                    b=TupleType(
                        [
                            wrapped_felt_type,
                            TupleType(
                                [
                                    ArrayType(FeltType()),
                                    ArrayType(wrapped_felt_type),
                                ]
                            ),
                        ]
                    ),
                )
            ),
        ),
    ],
)
def test_parse_with_defined_types(type_string, expected):
    types = {
        "Uint256": uint256_type,
        "WrappedFelt": wrapped_felt_type,
    }
    parsed = TypeParser(types).parse_inline_type(type_string)
    assert parsed == expected


def test_code_offset():
    with pytest.raises(UnknownTypeError) as err_info:
        TypeParser({}).parse_inline_type("codeoffset")

    assert err_info.value.type_name == "codeoffset"


def test_missing_type():
    with pytest.raises(UnknownTypeError) as err_info:
        TypeParser({}).parse_inline_type("Uint256")

    assert err_info.value.type_name == "Uint256"
    assert str(err_info.value) == "Type 'Uint256' is not defined"
