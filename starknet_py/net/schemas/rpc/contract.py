import json
from typing import Any, Optional

from marshmallow import EXCLUDE, ValidationError, fields, post_load, validate

from starknet_py.abi.v0.schemas import ContractAbiEntrySchema
from starknet_py.net.client_models import (
    AllocConstantSize,
    AllocConstantSizeInner,
    AllocFelt252Dict,
    AllocFelt252DictInner,
    AllocSegment,
    AllocSegmentInner,
    AssertAllAccessesUsed,
    AssertAllAccessesUsedInner,
    AssertAllKeysUsed,
    AssertCurrentAccessIndicesIsEmpty,
    AssertLeAssertThirdArcExcluded,
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
    CasmClassEntryPoint,
    CasmClassEntryPointsByType,
    CellRef,
    Cheatcode,
    CheatcodeInner,
    DebugPrint,
    DebugPrintInner,
    DeployedContract,
    DeprecatedCompiledContract,
    DeprecatedContractClass,
    Deref,
    DivMod,
    DivModInner,
    DoubleDeref,
    EntryPoint,
    EntryPointsByType,
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
    SierraCompiledContract,
    SierraContractClass,
    SierraEntryPoint,
    SierraEntryPointsByType,
    SquareRoot,
    SquareRootInner,
    SyncStatus,
    SystemCall,
    SystemCallInner,
    TestLessThan,
    TestLessThanInner,
    TestLessThanOrEqual,
    TestLessThanOrEqualInner,
    TestLessThenOrEqualAddress,
    TestLessThenOrEqualAddressInner,
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
from starknet_py.net.schemas.common import Felt, NumberAsHex
from starknet_py.utils.schema import Schema


class SyncStatusSchema(Schema):
    starting_block_hash = Felt(data_key="starting_block_hash", required=True)
    starting_block_num = Felt(data_key="starting_block_num", required=True)
    current_block_hash = Felt(data_key="current_block_hash", required=True)
    current_block_num = Felt(data_key="current_block_num", required=True)
    highest_block_hash = Felt(data_key="highest_block_hash", required=True)
    highest_block_num = Felt(data_key="highest_block_num", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SyncStatus:
        return SyncStatus(**data)


class ContractDiffSchema(Schema):
    address = Felt(data_key="address", required=True)
    contract_hash = Felt(data_key="contract_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployedContract:
        return DeployedContract(**data)


class SierraEntryPointSchema(Schema):
    selector = Felt(data_key="selector", required=True)
    function_idx = fields.Integer(data_key="function_idx", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraEntryPoint:
        return SierraEntryPoint(**data)


class EntryPointSchema(Schema):
    offset = NumberAsHex(data_key="offset", required=True)
    selector = Felt(data_key="selector", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPoint:
        return EntryPoint(**data)


class SierraEntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="CONSTRUCTOR", required=True
    )
    external = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="EXTERNAL", required=True
    )
    l1_handler = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="L1_HANDLER", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraEntryPointsByType:
        return SierraEntryPointsByType(**data)


class EntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(EntryPointSchema()), data_key="CONSTRUCTOR", required=True
    )
    external = fields.List(
        fields.Nested(EntryPointSchema()), data_key="EXTERNAL", required=True
    )
    l1_handler = fields.List(
        fields.Nested(EntryPointSchema()), data_key="L1_HANDLER", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPointsByType:
        return EntryPointsByType(**data)


class SierraContractClassSchema(Schema):
    sierra_program = fields.List(Felt(), data_key="sierra_program", required=True)
    contract_class_version = fields.String(
        data_key="contract_class_version", required=True
    )
    entry_points_by_type = fields.Nested(
        SierraEntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.String(data_key="abi", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraContractClass:
        return SierraContractClass(**data)


class ContractClassSchema(Schema):
    program = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(load_default=None),
        data_key="program",
        required=True,
    )
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.List(fields.Dict(), data_key="abi")

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeprecatedContractClass:
        return DeprecatedContractClass(**data)


class DeprecatedContractClassSchema(Schema):
    program = fields.String(data_key="program", required=True)
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.List(
        fields.Nested(ContractAbiEntrySchema(unknown=EXCLUDE)), data_key="abi"
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeprecatedContractClass:
        return DeprecatedContractClass(**data)


class DeprecatedCompiledContractSchema(ContractClassSchema):
    abi = fields.List(fields.Dict(), data_key="abi", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeprecatedCompiledContract:
        return DeprecatedCompiledContract(**data)


class CasmClassEntryPointSchema(Schema):
    selector = Felt(data_key="selector", required=True)
    offset = NumberAsHex(data_key="offset", required=True)
    builtins = fields.List(fields.String(), data_key="builtins")

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClassEntryPoint:
        return CasmClassEntryPoint(**data)


class CasmClassEntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="CONSTRUCTOR",
        required=True,
    )
    external = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="EXTERNAL",
        required=True,
    )
    l1_handler = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="L1_HANDLER",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClassEntryPointsByType:
        return CasmClassEntryPointsByType(**data)


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
            if DerefSchema.deref.data_key in value:
                return DerefSchema().load(value)
            elif ImmediateSchema.immediate.data_key in value:
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
            if DerefSchema.deref.data_key in value:
                return DerefSchema().load(value)
            elif DoubleDerefSchema.double_deref.data_key in value:
                return DoubleDerefSchema().load(value)
            elif ImmediateSchema.immediate.data_key in value:
                return ImmediateSchema().load(value)
            elif BinOpSchema.bin_op.data_key in value:
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


class TestLessThenOrEqualAddressInnerSchema(TestLessThanInnerSchema):
    pass

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThenOrEqualAddressInner:
        return TestLessThenOrEqualAddressInner(**data)


class TestLessThenOrEqualAddressSchema(Schema):
    test_less_than_or_equal_address = fields.Nested(
        TestLessThenOrEqualAddressInnerSchema(),
        data_key="TestLessThenOrEqualAddress",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TestLessThenOrEqualAddress:
        return TestLessThenOrEqualAddress(**data)


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
    dividend_0 = ResOperandField(data_key="dividend0", required=True)
    dividend_1 = ResOperandField(data_key="dividend1", required=True)
    divisor_0 = ResOperandField(data_key="divisor0", required=True)
    divisor_1 = ResOperandField(data_key="divisor1", required=True)
    quotient_0 = fields.Nested(CellRefSchema(), data_key="quotient0", required=True)
    quotient_1 = fields.Nested(CellRefSchema(), data_key="quotient1", required=True)
    remainder_0 = fields.Nested(CellRefSchema(), data_key="remainder0", required=True)
    remainder_1 = fields.Nested(CellRefSchema(), data_key="remainder1", required=True)

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
    dividend_0 = ResOperandField(data_key="dividend0", required=True)
    dividend_1 = ResOperandField(data_key="dividend1", required=True)
    dividend_2 = ResOperandField(data_key="dividend2", required=True)
    dividend_3 = ResOperandField(data_key="dividend3", required=True)
    divisor_0 = ResOperandField(data_key="divisor0", required=True)
    divisor_1 = ResOperandField(data_key="divisor1", required=True)
    quotient_0 = fields.Nested(CellRefSchema(), data_key="quotient0", required=True)
    quotient_1 = fields.Nested(CellRefSchema(), data_key="quotient1", required=True)
    quotient_2 = fields.Nested(CellRefSchema(), data_key="quotient2", required=True)
    quotient_3 = fields.Nested(CellRefSchema(), data_key="quotient3", required=True)
    remainder_0 = fields.Nested(CellRefSchema(), data_key="remainder0", required=True)
    remainder_1 = fields.Nested(CellRefSchema(), data_key="remainder1", required=True)

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
    sqrt_0 = fields.Nested(CellRefSchema(), data_key="sqrt0", required=True)
    sqrt_1 = fields.Nested(CellRefSchema(), data_key="sqrt1", required=True)
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
    dict_index = ResOperandField(data_key="dict_index", required=True)

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
    dict_access = ResOperandField(data_key="dict_access", required=True)
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
    index_delta_minus_1 = fields.Nested(
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
    b_0 = ResOperandField(data_key="b0", required=True)
    b_1 = ResOperandField(data_key="b1", required=True)
    n_0 = ResOperandField(data_key="n0", required=True)
    n_1 = ResOperandField(data_key="n1", required=True)
    g_0_or_no_inv = fields.Nested(
        CellRefSchema(), data_key="g0_or_no_inv", required=True
    )
    g_1_option = fields.Nested(CellRefSchema(), data_key="g1_option", required=True)
    s_or_r_0 = fields.Nested(CellRefSchema(), data_key="s_or_r0", required=True)
    s_or_r_1 = fields.Nested(CellRefSchema(), data_key="s_or_r1", required=True)
    t_or_k_0 = fields.Nested(CellRefSchema(), data_key="t_or_k0", required=True)
    t_or_k_1 = fields.Nested(CellRefSchema(), data_key="t_or_k1", required=True)

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


class HintField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            if value in AssertCurrentAccessIndicesIsEmpty:
                return AssertCurrentAccessIndicesIsEmpty(value)
            elif value in AssertAllKeysUsed:
                return AssertAllKeysUsed(value)
            elif value in AssertLeAssertThirdArcExcluded:
                return AssertLeAssertThirdArcExcluded(value)

        elif isinstance(value, dict) and len(value.keys()) == 1:
            key_to_schema_mapping = {
                AssertAllAccessesUsedSchema.assert_all_accesses_used.data_key: AssertAllAccessesUsedSchema,
                AssertLtAssertValidInputSchema.assert_lt_assert_valid_input.data_key: AssertLtAssertValidInputSchema,
                Felt252DictReadSchema.felt252_dict_read.data_key: Felt252DictReadSchema,
                Felt252DictWriteSchema.felt252_dict_write.data_key: Felt252DictWriteSchema,
                AllocSegmentSchema.alloc_segment.data_key: AllocSegmentSchema,
                TestLessThanSchema.test_less_than.data_key: TestLessThanSchema,
                TestLessThanOrEqualSchema.test_less_than_or_equal.data_key: TestLessThanOrEqualSchema,
                TestLessThenOrEqualAddressSchema.test_less_than_or_equal_address.data_key: TestLessThenOrEqualAddressSchema,
                WideMul128Schema.wide_mul128.data_key: WideMul128Schema,
                DivModSchema.div_mod.data_key: DivModSchema,
                Uint256DivModSchema.uint256_div_mod.data_key: Uint256DivModSchema,
                Uint512DivModByUint256Schema.uint512_div_mod_by_uint256.data_key: Uint512DivModByUint256Schema,
                SquareRootSchema.square_root.data_key: SquareRootSchema,
                Uint256SquareRootSchema.uint256_square_root.data_key: Uint256SquareRootSchema,
                LinearSplitSchema.linear_split.data_key: LinearSplitSchema,
                AllocFelt252DictSchema.alloc_felt252_dict.data_key: AllocFelt252DictSchema,
                Felt252DictEntryInitSchema.felt252_dict_entry_init.data_key: Felt252DictEntryInitSchema,
                Felt252DictEntryUpdateSchema.felt252_dict_entry_update.data_key: Felt252DictEntryUpdateSchema,
                GetSegmentArenaIndexSchema.get_segment_arena_index.data_key: GetSegmentArenaIndexSchema,
                InitSquashDataSchema.init_squash_data.data_key: InitSquashDataSchema,
                GetCurrentAccessIndexSchema.get_current_access_index.data_key: GetCurrentAccessIndexSchema,
                ShouldSkipSquashLoopSchema.should_skip_squash_loop.data_key: ShouldSkipSquashLoopSchema,
                GetCurrentAccessDeltaSchema.get_current_access_delta.data_key: GetCurrentAccessDeltaSchema,
                ShouldContinueSquashLoopSchema.should_continue_squash_loop.data_key: ShouldContinueSquashLoopSchema,
                GetNextDictKeySchema.get_next_dict_key.data_key: GetNextDictKeySchema,
                AssertLeFindSmallArcsSchema.assert_le_find_small_arcs.data_key: AssertLeFindSmallArcsSchema,
                AssertLeIsFirstArcExcludedSchema.assert_le_is_first_arc_excluded.data_key: AssertLeIsFirstArcExcludedSchema,
                AssertLeIsSecondArcExcludedSchema.assert_le_is_second_arc_excluded.data_key: AssertLeIsSecondArcExcludedSchema,
                RandomEcPointSchema.random_ec_point.data_key: RandomEcPointSchema,
                FieldSqrtSchema.field_sqrt.data_key: FieldSqrtSchema,
                DebugPrintSchema.debug_print.data_key: DebugPrintSchema,
                AllocConstantSizeSchema.alloc_constant_size.data_key: AllocConstantSizeSchema,
                U256InvModNSchema.u256_inv_mod_n.data_key: U256InvModNSchema,
                EvalCircuitSchema.eval_circuit.data_key: EvalCircuitSchema,
                SystemCallSchema.system_call.data_key: SystemCallSchema,
                CheatcodeSchema.cheatcode.data_key: CheatcodeSchema,
            }

            key = list(value.keys())[0]
            schema_cls = key_to_schema_mapping.get(key)

            if schema_cls is not None:
                return schema_cls().load(value)

        raise ValidationError(f"Invalid value provided for Hint: {value}.")

    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs):
        if isinstance(value, AssertCurrentAccessIndicesIsEmpty):
            return str(value.value)
        elif isinstance(value, AssertAllKeysUsed):
            return str(value.value)
        elif isinstance(value, AssertLeAssertThirdArcExcluded):
            return str(value.value)

        model_to_schema_mapping = {
            AllocConstantSize: AllocConstantSizeSchema,
            AllocFelt252Dict: AllocFelt252DictSchema,
            AllocSegment: AllocSegmentSchema,
            AssertAllAccessesUsed: AssertAllAccessesUsedSchema,
            AssertLeFindSmallArcs: AssertLeFindSmallArcsSchema,
            AssertLeIsFirstArcExcluded: AssertLeIsFirstArcExcludedSchema,
            AssertLeIsSecondArcExcluded: AssertLeIsSecondArcExcludedSchema,
            AssertLtAssertValidInput: AssertLtAssertValidInputSchema,
            BinOp: BinOpSchema,
            Cheatcode: CheatcodeSchema,
            DebugPrint: DebugPrintSchema,
            Deref: DerefSchema,
            DivMod: DivModSchema,
            DoubleDeref: DoubleDerefSchema,
            EvalCircuit: EvalCircuitSchema,
            Felt252DictEntryInit: Felt252DictEntryInitSchema,
            Felt252DictEntryUpdate: Felt252DictEntryUpdateSchema,
            Felt252DictRead: Felt252DictReadSchema,
            Felt252DictWrite: Felt252DictWriteSchema,
            FieldSqrt: FieldSqrtSchema,
            GetCurrentAccessDelta: GetCurrentAccessDeltaSchema,
            GetCurrentAccessIndex: GetCurrentAccessIndexSchema,
            GetNextDictKey: GetNextDictKeySchema,
            GetSegmentArenaIndex: GetSegmentArenaIndexSchema,
            Immediate: ImmediateSchema,
            InitSquashData: InitSquashDataSchema,
            LinearSplit: LinearSplitSchema,
            RandomEcPoint: RandomEcPointSchema,
            ShouldContinueSquashLoop: ShouldContinueSquashLoopSchema,
            ShouldSkipSquashLoop: ShouldSkipSquashLoopSchema,
            SquareRoot: SquareRootSchema,
            SystemCall: SystemCallSchema,
            TestLessThan: TestLessThanSchema,
            TestLessThanOrEqual: TestLessThanOrEqualSchema,
            TestLessThenOrEqualAddress: TestLessThenOrEqualAddressSchema,
            U256InvModN: U256InvModNSchema,
            Uint256DivMod: Uint256DivModSchema,
            Uint256SquareRoot: Uint256SquareRootSchema,
            Uint512DivModByUint256: Uint512DivModByUint256Schema,
            WideMul128: WideMul128Schema,
        }

        schema_cls = model_to_schema_mapping.get(type(value))

        if schema_cls is not None:
            schema = schema_cls()
            return schema.dump(value)

        raise ValidationError(
            f"Invalid value provided for {self.__class__.__name__}: {value}."
        )


class CasmClassSchema(Schema):
    prime = NumberAsHex(data_key="prime", required=True)
    bytecode = fields.List(Felt(), data_key="bytecode", required=True)
    bytecode_segment_lengths = fields.List(
        fields.Integer(), data_key="bytecode_segment_lengths", load_default=None
    )
    hints = fields.List(
        fields.Tuple(
            (fields.Integer(), HintField()),
        ),
        data_key="hints",
        required=True,
    )
    compiler_version = fields.String(data_key="compiler_version", required=True)
    entry_points_by_type = fields.Nested(
        CasmClassEntryPointsByTypeSchema(),
        data_key="entry_points_by_type",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClass:
        return CasmClass(**data)


class AbiField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            return value
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return json.dumps(value)
        raise ValidationError("Field should be str or list[dict].")


class SierraCompiledContractSchema(SierraContractClassSchema):
    abi = AbiField(data_key="abi", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraCompiledContract:
        return SierraCompiledContract(**data)
