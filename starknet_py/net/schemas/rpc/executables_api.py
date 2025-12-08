from typing import Any, Optional

from marshmallow import ValidationError, fields, post_load, validate

from starknet_py.net.executable_models import (
    AllocConstantSize,
    AllocConstantSizeInner,
    AllocFelt252Dict,
    AllocFelt252DictInner,
    AllocSegment,
    AllocSegmentInner,
    AssertAllAccessesUsed,
    AssertAllAccessesUsedInner,
    AssertLeFindSmallArcs,
    AssertLeFindSmallArcsInner,
    AssertLeIsFirstArcExcluded,
    AssertLeIsFirstArcExcludedInner,
    AssertLeIsSecondArcExcluded,
    AssertLeIsSecondArcExcludedInner,
    AssertLtAssertValidInput,
    AssertLtAssertValidInputInner,
    BinOp,
    BinOpInner,
    CasmClass,
    CasmClassEntryPointsByType,
    CellRef,
    Cheatcode,
    CheatcodeInner,
    DebugPrint,
    DebugPrintInner,
    Deref,
    DivMod,
    DivModInner,
    DoubleDeref,
    EvalCircuit,
    EvalCircuitInner,
    Felt252DictEntryInit,
    Felt252DictEntryInitInner,
    Felt252DictEntryUpdate,
    Felt252DictEntryUpdateInner,
    Felt252DictRead,
    Felt252DictReadInner,
    Felt252DictWrite,
    Felt252DictWriteInner,
    FieldSqrt,
    FieldSqrtInner,
    GetCurrentAccessDelta,
    GetCurrentAccessDeltaInner,
    GetCurrentAccessIndex,
    GetCurrentAccessIndexInner,
    GetNextDictKey,
    GetNextDictKeyInner,
    GetSegmentArenaIndex,
    GetSegmentArenaIndexInner,
    Hint,
    Immediate,
    InitSquashData,
    InitSquashDataInner,
    LinearSplit,
    LinearSplitInner,
    RandomEcPoint,
    RandomEcPointInner,
    ShouldContinueSquashLoop,
    ShouldContinueSquashLoopInner,
    ShouldSkipSquashLoop,
    ShouldSkipSquashLoopInner,
    SquareRoot,
    SquareRootInner,
    SystemCall,
    SystemCallInner,
    TestLessThan,
    TestLessThanInner,
    TestLessThanOrEqual,
    TestLessThanOrEqualAddress,
    TestLessThanOrEqualAddressInner,
    TestLessThanOrEqualInner,
    U256InvModN,
    U256InvModNInner,
    Uint256DivMod,
    Uint256DivModInner,
    Uint256SquareRoot,
    Uint256SquareRootInner,
    Uint512DivModByUint256,
    Uint512DivModByUint256Inner,
    WideMul128,
    WideMul128Inner,
)
from starknet_py.net.schemas.common import NumberAsHex
from starknet_py.utils.schema import Schema


class CellRefSchema(Schema):
    register = fields.String(
        data_key="register", validate=validate.OneOf(["AP", "FP"]), required=True
    )
    offset = fields.Integer(data_key="offset", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> CellRef:
        return CellRef(**data)


class AssertAllAccessesUsedInnerSchema(Schema):
    n_used_accesses = fields.Nested(
        CellRefSchema(), data_key="n_used_accesses", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertAllAccessesUsedInner:
        return AssertAllAccessesUsedInner(**data)


class AssertAllAccessesUsedSchema(Schema):
    assert_all_accesses_used = fields.Nested(
        AssertAllAccessesUsedInnerSchema(),
        data_key="AssertAllAccessesUsed",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertAllAccessesUsed:
        return AssertAllAccessesUsed(**data)


class DerefSchema(Schema):
    deref = fields.Nested(CellRefSchema(), data_key="Deref", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Deref:
        return Deref(**data)


class DoubleDerefSchema(Schema):
    double_deref = fields.Tuple(
        (fields.Nested(CellRefSchema()), fields.Integer()),
        data_key="DoubleDeref",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DoubleDeref:
        return DoubleDeref(**data)


class ImmediateSchema(Schema):
    immediate = NumberAsHex(data_key="Immediate", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Immediate:
        return Immediate(**data)


class BinOpBField(fields.Field):
    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs):
        if isinstance(value, Deref):
            return DerefSchema().dump(value)
        elif isinstance(value, Immediate):
            return ImmediateSchema().dump(value)

        raise ValidationError(
            f"Invalid value provided for {self.__class__.__name__}: {value}."
        )

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict):
            if "Deref" in value:
                return DerefSchema().load(value)
            elif "Immediate" in value:
                return ImmediateSchema().load(value)

        raise ValidationError(
            f"Invalid value provided for 'b': {value}. Must be a Deref or an Immediate object."
        )


class BinOpInnerSchema(Schema):
    op = fields.String(
        data_key="op", required=True, validate=validate.OneOf(["Add", "Mul"])
    )
    a = fields.Nested(CellRefSchema(), data_key="a", required=True)
    b = BinOpBField(data_key="b", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BinOpInner:
        return BinOpInner(**data)


class BinOpSchema(Schema):
    bin_op = fields.Nested(BinOpInnerSchema(), data_key="BinOp", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BinOp:
        return BinOp(**data)


class ResOperandField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, Deref):
            return DerefSchema().dump(value)
        elif isinstance(value, DoubleDeref):
            return DoubleDerefSchema().dump(value)
        elif isinstance(value, Immediate):
            return ImmediateSchema().dump(value)
        elif isinstance(value, BinOp):
            return BinOpSchema().dump(value)

        raise ValidationError(
            f"Invalid value provided for {self.__class__.__name__}: {value}."
        )

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict):
            if "Deref" in value:
                return DerefSchema().load(value)
            elif "DoubleDeref" in value:
                return DoubleDerefSchema().load(value)
            elif "Immediate" in value:
                return ImmediateSchema().load(value)
            elif "BinOp" in value:
                return BinOpSchema().load(value)

        raise ValidationError(f"Invalid value provided for ResOperand: {value}.")


class AssertLtAssertValidInputInnerSchema(Schema):
    a = ResOperandField(data_key="a", required=True)
    b = ResOperandField(data_key="b", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLtAssertValidInputInner:
        return AssertLtAssertValidInputInner(**data)


class AssertLtAssertValidInputSchema(Schema):
    assert_lt_assert_valid_input = fields.Nested(
        AssertLtAssertValidInputInnerSchema(),
        data_key="AssertLtAssertValidInput",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLtAssertValidInput:
        return AssertLtAssertValidInput(**data)


class Felt252DictReadInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    key = ResOperandField(data_key="key", required=True)
    value_dst = fields.Nested(CellRefSchema(), data_key="value_dst", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictReadInner:
        return Felt252DictReadInner(**data)


class Felt252DictReadSchema(Schema):
    felt252_dict_read = fields.Nested(
        Felt252DictReadInnerSchema(), data_key="Felt252DictRead", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictRead:
        return Felt252DictRead(**data)


class Felt252DictWriteInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    key = ResOperandField(data_key="key", required=True)
    value = ResOperandField(data_key="value", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictWriteInner:
        return Felt252DictWriteInner(**data)


class Felt252DictWriteSchema(Schema):
    felt252_dict_write = fields.Nested(
        Felt252DictWriteInnerSchema(), data_key="Felt252DictWrite", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictWrite:
        return Felt252DictWrite(**data)


class AllocSegmentInnerSchema(Schema):
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> AllocSegmentInner:
        return AllocSegmentInner(**data)


class AllocSegmentSchema(Schema):
    alloc_segment = fields.Nested(
        AllocSegmentInnerSchema(), data_key="AllocSegment", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AllocSegment:
        return AllocSegment(**data)


class TestLessThanInnerSchema(Schema):
    lhs = ResOperandField(data_key="lhs", required=True)
    rhs = ResOperandField(data_key="rhs", required=True)
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThanInner:
        return TestLessThanInner(**data)


class TestLessThanSchema(Schema):
    test_less_than = fields.Nested(
        TestLessThanInnerSchema(), data_key="TestLessThan", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThan:
        return TestLessThan(**data)


class TestLessThanOrEqualInnerSchema(TestLessThanInnerSchema):
    pass

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThanOrEqualInner:
        return TestLessThanOrEqualInner(**data)


class TestLessThanOrEqualSchema(Schema):
    test_less_than_or_equal = fields.Nested(
        TestLessThanOrEqualInnerSchema(), data_key="TestLessThanOrEqual", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThanOrEqual:
        return TestLessThanOrEqual(**data)


class TestLessThanOrEqualAddressInnerSchema(TestLessThanInnerSchema):
    pass

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThanOrEqualAddressInner:
        return TestLessThanOrEqualAddressInner(**data)


class TestLessThanOrEqualAddressSchema(Schema):
    test_less_than_or_equal_address = fields.Nested(
        TestLessThanOrEqualAddressInnerSchema(),
        data_key="TestLessThanOrEqualAddress",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThanOrEqualAddress:
        return TestLessThanOrEqualAddress(**data)


class WideMul128InnerSchema(Schema):
    lhs = ResOperandField(data_key="lhs", required=True)
    rhs = ResOperandField(data_key="rhs", required=True)
    high = fields.Nested(CellRefSchema(), data_key="high", required=True)
    low = fields.Nested(CellRefSchema(), data_key="low", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> WideMul128Inner:
        return WideMul128Inner(**data)


class WideMul128Schema(Schema):
    wide_mul128 = fields.Nested(
        WideMul128InnerSchema(), data_key="WideMul128", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> WideMul128:
        return WideMul128(**data)


class DivModInnerSchema(Schema):
    lhs = ResOperandField(data_key="lhs", required=True)
    rhs = ResOperandField(data_key="rhs", required=True)
    quotient = fields.Nested(CellRefSchema(), data_key="quotient", required=True)
    remainder = fields.Nested(CellRefSchema(), data_key="remainder", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DivModInner:
        return DivModInner(**data)


class DivModSchema(Schema):
    div_mod = fields.Nested(DivModInnerSchema(), data_key="DivMod", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DivMod:
        return DivMod(**data)


class Uint256DivModInnerSchema(Schema):
    dividend0 = ResOperandField(data_key="dividend0", required=True)
    dividend1 = ResOperandField(data_key="dividend1", required=True)
    divisor0 = ResOperandField(data_key="divisor0", required=True)
    divisor1 = ResOperandField(data_key="divisor1", required=True)
    quotient0 = fields.Nested(CellRefSchema(), data_key="quotient0", required=True)
    quotient1 = fields.Nested(CellRefSchema(), data_key="quotient1", required=True)
    remainder0 = fields.Nested(CellRefSchema(), data_key="remainder0", required=True)
    remainder1 = fields.Nested(CellRefSchema(), data_key="remainder1", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Uint256DivModInner:
        return Uint256DivModInner(**data)


class Uint256DivModSchema(Schema):
    uint256_div_mod = fields.Nested(
        Uint256DivModInnerSchema(), data_key="Uint256DivMod", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Uint256DivMod:
        return Uint256DivMod(**data)


class Uint512DivModByUint256InnerSchema(Schema):
    dividend0 = ResOperandField(data_key="dividend0", required=True)
    dividend1 = ResOperandField(data_key="dividend1", required=True)
    dividend2 = ResOperandField(data_key="dividend2", required=True)
    dividend3 = ResOperandField(data_key="dividend3", required=True)
    divisor0 = ResOperandField(data_key="divisor0", required=True)
    divisor1 = ResOperandField(data_key="divisor1", required=True)
    quotient0 = fields.Nested(CellRefSchema(), data_key="quotient0", required=True)
    quotient1 = fields.Nested(CellRefSchema(), data_key="quotient1", required=True)
    quotient2 = fields.Nested(CellRefSchema(), data_key="quotient2", required=True)
    quotient3 = fields.Nested(CellRefSchema(), data_key="quotient3", required=True)
    remainder0 = fields.Nested(CellRefSchema(), data_key="remainder0", required=True)
    remainder1 = fields.Nested(CellRefSchema(), data_key="remainder1", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Uint512DivModByUint256Inner:
        return Uint512DivModByUint256Inner(**data)


class Uint512DivModByUint256Schema(Schema):
    uint512_div_mod_by_uint256 = fields.Nested(
        Uint512DivModByUint256InnerSchema(),
        data_key="Uint512DivModByUint256",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Uint512DivModByUint256:
        return Uint512DivModByUint256(**data)


class SquareRootInnerSchema(Schema):
    value = ResOperandField(data_key="value", required=True)
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SquareRootInner:
        return SquareRootInner(**data)


class SquareRootSchema(Schema):
    square_root = fields.Nested(
        SquareRootInnerSchema(), data_key="SquareRoot", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> SquareRoot:
        return SquareRoot(**data)


class Uint256SquareRootInnerSchema(Schema):
    value_low = ResOperandField(data_key="value_low", required=True)
    value_high = ResOperandField(data_key="value_high", required=True)
    sqrt0 = fields.Nested(CellRefSchema(), data_key="sqrt0", required=True)
    sqrt1 = fields.Nested(CellRefSchema(), data_key="sqrt1", required=True)
    remainder_low = fields.Nested(
        CellRefSchema(), data_key="remainder_low", required=True
    )
    remainder_high = fields.Nested(
        CellRefSchema(), data_key="remainder_high", required=True
    )
    sqrt_mul_2_minus_remainder_ge_u128 = fields.Nested(
        CellRefSchema(), data_key="sqrt_mul_2_minus_remainder_ge_u128", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Uint256SquareRootInner:
        return Uint256SquareRootInner(**data)


class Uint256SquareRootSchema(Schema):
    uint256_square_root = fields.Nested(
        Uint256SquareRootInnerSchema(), data_key="Uint256SquareRoot", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Uint256SquareRoot:
        return Uint256SquareRoot(**data)


class LinearSplitInnerSchema(Schema):
    value = ResOperandField(data_key="value", required=True)
    scalar = ResOperandField(data_key="scalar", required=True)
    max_x = ResOperandField(data_key="max_x", required=True)
    x = fields.Nested(CellRefSchema(), data_key="x", required=True)
    y = fields.Nested(CellRefSchema(), data_key="y", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> LinearSplitInner:
        return LinearSplitInner(**data)


class LinearSplitSchema(Schema):
    linear_split = fields.Nested(
        LinearSplitInnerSchema(), data_key="LinearSplit", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> LinearSplit:
        return LinearSplit(**data)


class AllocFelt252DictInnerSchema(Schema):
    segment_arena_ptr = ResOperandField(data_key="segment_arena_ptr", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> AllocFelt252DictInner:
        return AllocFelt252DictInner(**data)


class AllocFelt252DictSchema(Schema):
    alloc_felt252_dict = fields.Nested(
        AllocFelt252DictInnerSchema(), data_key="AllocFelt252Dict", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AllocFelt252Dict:
        return AllocFelt252Dict(**data)


class Felt252DictEntryInitInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    key = ResOperandField(data_key="key", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictEntryInitInner:
        return Felt252DictEntryInitInner(**data)


class Felt252DictEntryInitSchema(Schema):
    felt252_dict_entry_init = fields.Nested(
        Felt252DictEntryInitInnerSchema(),
        data_key="Felt252DictEntryInit",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictEntryInit:
        return Felt252DictEntryInit(**data)


class Felt252DictEntryUpdateInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    value = ResOperandField(data_key="value", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictEntryUpdateInner:
        return Felt252DictEntryUpdateInner(**data)


class Felt252DictEntryUpdateSchema(Schema):
    felt252_dict_entry_update = fields.Nested(
        Felt252DictEntryUpdateInnerSchema(),
        data_key="Felt252DictEntryUpdate",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Felt252DictEntryUpdate:
        return Felt252DictEntryUpdate(**data)


class GetSegmentArenaIndexInnerSchema(Schema):
    dict_end_ptr = ResOperandField(data_key="dict_end_ptr", required=True)
    dict_index = fields.Nested(CellRefSchema(), data_key="dict_index", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetSegmentArenaIndexInner:
        return GetSegmentArenaIndexInner(**data)


class GetSegmentArenaIndexSchema(Schema):
    get_segment_arena_index = fields.Nested(
        GetSegmentArenaIndexInnerSchema(),
        data_key="GetSegmentArenaIndex",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetSegmentArenaIndex:
        return GetSegmentArenaIndex(**data)


class InitSquashDataInnerSchema(Schema):
    dict_accesses = ResOperandField(data_key="dict_accesses", required=True)
    ptr_diff = ResOperandField(data_key="ptr_diff", required=True)
    n_accesses = ResOperandField(data_key="n_accesses", required=True)
    big_keys = fields.Nested(CellRefSchema(), data_key="big_keys", required=True)
    first_key = fields.Nested(CellRefSchema(), data_key="first_key", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> InitSquashDataInner:
        return InitSquashDataInner(**data)


class InitSquashDataSchema(Schema):
    init_squash_data = fields.Nested(
        InitSquashDataInnerSchema(), data_key="InitSquashData", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> InitSquashData:
        return InitSquashData(**data)


class GetCurrentAccessIndexInnerSchema(Schema):
    range_check_ptr = ResOperandField(data_key="range_check_ptr", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetCurrentAccessIndexInner:
        return GetCurrentAccessIndexInner(**data)


class GetCurrentAccessIndexSchema(Schema):
    get_current_access_index = fields.Nested(
        GetCurrentAccessIndexInnerSchema(),
        data_key="GetCurrentAccessIndex",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetCurrentAccessIndex:
        return GetCurrentAccessIndex(**data)


class ShouldSkipSquashLoopInnerSchema(Schema):
    should_skip_loop = fields.Nested(
        CellRefSchema(), data_key="should_skip_loop", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ShouldSkipSquashLoopInner:
        return ShouldSkipSquashLoopInner(**data)


class ShouldSkipSquashLoopSchema(Schema):
    should_skip_squash_loop = fields.Nested(
        ShouldSkipSquashLoopInnerSchema(),
        data_key="ShouldSkipSquashLoop",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ShouldSkipSquashLoop:
        return ShouldSkipSquashLoop(**data)


class GetCurrentAccessDeltaInnerSchema(Schema):
    index_delta_minus1 = fields.Nested(
        CellRefSchema(), data_key="index_delta_minus1", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetCurrentAccessDeltaInner:
        return GetCurrentAccessDeltaInner(**data)


class GetCurrentAccessDeltaSchema(Schema):
    get_current_access_delta = fields.Nested(
        GetCurrentAccessDeltaInnerSchema(),
        data_key="GetCurrentAccessDelta",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetCurrentAccessDelta:
        return GetCurrentAccessDelta(**data)


class ShouldContinueSquashLoopInnerSchema(Schema):
    should_continue = fields.Nested(
        CellRefSchema(), data_key="should_continue", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ShouldContinueSquashLoopInner:
        return ShouldContinueSquashLoopInner(**data)


class ShouldContinueSquashLoopSchema(Schema):
    should_continue_squash_loop = fields.Nested(
        ShouldContinueSquashLoopInnerSchema(),
        data_key="ShouldContinueSquashLoop",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ShouldContinueSquashLoop:
        return ShouldContinueSquashLoop(**data)


class GetNextDictKeyInnerSchema(Schema):
    next_key = fields.Nested(CellRefSchema(), data_key="next_key", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetNextDictKeyInner:
        return GetNextDictKeyInner(**data)


class GetNextDictKeySchema(Schema):
    get_next_dict_key = fields.Nested(
        GetNextDictKeyInnerSchema(), data_key="GetNextDictKey", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> GetNextDictKey:
        return GetNextDictKey(**data)


class AssertLeFindSmallArcsInnerSchema(Schema):
    range_check_ptr = ResOperandField(data_key="range_check_ptr", required=True)
    a = ResOperandField(data_key="a", required=True)
    b = ResOperandField(data_key="b", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLeFindSmallArcsInner:
        return AssertLeFindSmallArcsInner(**data)


class AssertLeFindSmallArcsSchema(Schema):
    assert_le_find_small_arcs = fields.Nested(
        AssertLeFindSmallArcsInnerSchema(),
        data_key="AssertLeFindSmallArcs",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLeFindSmallArcs:
        return AssertLeFindSmallArcs(**data)


class AssertLeIsFirstArcExcludedInnerSchema(Schema):
    skip_exclude_a_flag = fields.Nested(
        CellRefSchema(), data_key="skip_exclude_a_flag", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLeIsFirstArcExcludedInner:
        return AssertLeIsFirstArcExcludedInner(**data)


class AssertLeIsFirstArcExcludedSchema(Schema):
    assert_le_is_first_arc_excluded = fields.Nested(
        AssertLeIsFirstArcExcludedInnerSchema(),
        data_key="AssertLeIsFirstArcExcluded",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLeIsFirstArcExcluded:
        return AssertLeIsFirstArcExcluded(**data)


class AssertLeIsSecondArcExcludedInnerSchema(Schema):
    skip_exclude_b_minus_a = fields.Nested(
        CellRefSchema(), data_key="skip_exclude_b_minus_a", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLeIsSecondArcExcludedInner:
        return AssertLeIsSecondArcExcludedInner(**data)


class AssertLeIsSecondArcExcludedSchema(Schema):
    assert_le_is_second_arc_excluded = fields.Nested(
        AssertLeIsSecondArcExcludedInnerSchema(),
        data_key="AssertLeIsSecondArcExcluded",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AssertLeIsSecondArcExcluded:
        return AssertLeIsSecondArcExcluded(**data)


class RandomEcPointInnerSchema(Schema):
    x = fields.Nested(CellRefSchema(), data_key="x", required=True)
    y = fields.Nested(CellRefSchema(), data_key="y", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> RandomEcPointInner:
        return RandomEcPointInner(**data)


class RandomEcPointSchema(Schema):
    random_ec_point = fields.Nested(
        RandomEcPointInnerSchema(), data_key="RandomEcPoint", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> RandomEcPoint:
        return RandomEcPoint(**data)


class FieldSqrtInnerSchema(Schema):
    val = ResOperandField(data_key="val", required=True)
    sqrt = fields.Nested(CellRefSchema(), data_key="sqrt", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> FieldSqrtInner:
        return FieldSqrtInner(**data)


class FieldSqrtSchema(Schema):
    field_sqrt = fields.Nested(
        FieldSqrtInnerSchema(), data_key="FieldSqrt", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> FieldSqrt:
        return FieldSqrt(**data)


class DebugPrintInnerSchema(Schema):
    start = ResOperandField(data_key="start", required=True)
    end = ResOperandField(data_key="end", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DebugPrintInner:
        return DebugPrintInner(**data)


class DebugPrintSchema(Schema):
    debug_print = fields.Nested(
        DebugPrintInnerSchema(), data_key="DebugPrint", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DebugPrint:
        return DebugPrint(**data)


class AllocConstantSizeInnerSchema(Schema):
    size = ResOperandField(data_key="size", required=True)
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> AllocConstantSizeInner:
        return AllocConstantSizeInner(**data)


class AllocConstantSizeSchema(Schema):
    alloc_constant_size = fields.Nested(
        AllocConstantSizeInnerSchema(), data_key="AllocConstantSize", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> AllocConstantSize:
        return AllocConstantSize(**data)


class U256InvModNInnerSchema(Schema):
    b0 = ResOperandField(data_key="b0", required=True)
    b1 = ResOperandField(data_key="b1", required=True)
    n0 = ResOperandField(data_key="n0", required=True)
    n1 = ResOperandField(data_key="n1", required=True)
    g0_or_no_inv = fields.Nested(
        CellRefSchema(), data_key="g0_or_no_inv", required=True
    )
    g1_option = fields.Nested(CellRefSchema(), data_key="g1_option", required=True)
    s_or_r0 = fields.Nested(CellRefSchema(), data_key="s_or_r0", required=True)
    s_or_r1 = fields.Nested(CellRefSchema(), data_key="s_or_r1", required=True)
    t_or_k0 = fields.Nested(CellRefSchema(), data_key="t_or_k0", required=True)
    t_or_k1 = fields.Nested(CellRefSchema(), data_key="t_or_k1", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> U256InvModNInner:
        return U256InvModNInner(**data)


class U256InvModNSchema(Schema):
    u256_inv_mod_n = fields.Nested(
        U256InvModNInnerSchema(), data_key="U256InvModN", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> U256InvModN:
        return U256InvModN(**data)


class EvalCircuitInnerSchema(Schema):
    n_add_mods = ResOperandField(data_key="n_add_mods", required=True)
    add_mod_builtin = ResOperandField(data_key="add_mod_builtin", required=True)
    n_mul_mods = ResOperandField(data_key="n_mul_mods", required=True)
    mul_mod_builtin = ResOperandField(data_key="mul_mod_builtin", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EvalCircuitInner:
        return EvalCircuitInner(**data)


class EvalCircuitSchema(Schema):
    eval_circuit = fields.Nested(
        EvalCircuitInnerSchema(), data_key="EvalCircuit", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> EvalCircuit:
        return EvalCircuit(**data)


class SystemCallInnerSchema(Schema):
    system = ResOperandField(data_key="system", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SystemCallInner:
        return SystemCallInner(**data)


class SystemCallSchema(Schema):
    system_call = fields.Nested(
        SystemCallInnerSchema(), data_key="SystemCall", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> SystemCall:
        return SystemCall(**data)


class CheatcodeInnerSchema(Schema):
    selector = NumberAsHex(data_key="selector", required=True)
    input_start = ResOperandField(data_key="input_start", required=True)
    input_end = ResOperandField(data_key="input_end", required=True)
    output_start = fields.Nested(
        CellRefSchema(), data_key="output_start", required=True
    )
    output_end = fields.Nested(CellRefSchema(), data_key="output_end", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> CheatcodeInner:
        return CheatcodeInner(**data)


class CheatcodeSchema(Schema):
    cheatcode = fields.Nested(
        CheatcodeInnerSchema(), data_key="Cheatcode", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Cheatcode:
        return Cheatcode(**data)


HINT_TYPE_SCHEMAS_MAPPING = {
    "AllocConstantSize": AllocConstantSizeSchema,
    "AllocFelt252Dict": AllocFelt252DictSchema,
    "AllocSegment": AllocSegmentSchema,
    "AssertAllAccessesUsed": AssertAllAccessesUsedSchema,
    "AssertLeFindSmallArcs": AssertLeFindSmallArcsSchema,
    "AssertLeIsFirstArcExcluded": AssertLeIsFirstArcExcludedSchema,
    "AssertLeIsSecondArcExcluded": AssertLeIsSecondArcExcludedSchema,
    "AssertLtAssertValidInput": AssertLtAssertValidInputSchema,
    "BinOp": BinOpSchema,
    "Cheatcode": CheatcodeSchema,
    "DebugPrint": DebugPrintSchema,
    "Deref": DerefSchema,
    "DivMod": DivModSchema,
    "DoubleDeref": DoubleDerefSchema,
    "EvalCircuit": EvalCircuitSchema,
    "Felt252DictEntryInit": Felt252DictEntryInitSchema,
    "Felt252DictEntryUpdate": Felt252DictEntryUpdateSchema,
    "Felt252DictRead": Felt252DictReadSchema,
    "Felt252DictWrite": Felt252DictWriteSchema,
    "FieldSqrt": FieldSqrtSchema,
    "GetCurrentAccessDelta": GetCurrentAccessDeltaSchema,
    "GetCurrentAccessIndex": GetCurrentAccessIndexSchema,
    "GetNextDictKey": GetNextDictKeySchema,
    "GetSegmentArenaIndex": GetSegmentArenaIndexSchema,
    "Immediate": ImmediateSchema,
    "InitSquashData": InitSquashDataSchema,
    "LinearSplit": LinearSplitSchema,
    "RandomEcPoint": RandomEcPointSchema,
    "ShouldContinueSquashLoop": ShouldContinueSquashLoopSchema,
    "ShouldSkipSquashLoop": ShouldSkipSquashLoopSchema,
    "SquareRoot": SquareRootSchema,
    "SystemCall": SystemCallSchema,
    "TestLessThan": TestLessThanSchema,
    "TestLessThanOrEqual": TestLessThanOrEqualSchema,
    "TestLessThanOrEqualAddress": TestLessThanOrEqualAddressSchema,
    "U256InvModN": U256InvModNSchema,
    "Uint256DivMod": Uint256DivModSchema,
    "Uint256SquareRoot": Uint256SquareRootSchema,
    "Uint512DivModByUint256": Uint512DivModByUint256Schema,
    "WideMul128": WideMul128Schema,
}


class HintSchema(Schema):
    def load(self, data, *args, **kwargs) -> Hint:
        if not isinstance(data, dict) or len(data) != 1:
            raise ValidationError("Hint must be a dict with a single key.")

        key = next(iter(data))

        if key not in HINT_TYPE_SCHEMAS_MAPPING:
            raise ValidationError(f"Unknown Hint type: {key}")

        schema = HINT_TYPE_SCHEMAS_MAPPING[key]()

        return schema.load(data)

    def dump(self, obj, *args, **kwargs):
        if not isinstance(obj, dict) or len(obj) != 1:
            raise ValidationError("Hint must be a dict with a single key.")

        key = next(iter(obj))

        if key not in HINT_TYPE_SCHEMAS_MAPPING:
            raise ValidationError(f"Invalid value provided for Hint type: {key}")

        return {key: HINT_TYPE_SCHEMAS_MAPPING[key].dump(obj[key])}
