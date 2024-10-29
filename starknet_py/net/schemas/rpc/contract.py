import json
from enum import Enum

from marshmallow import EXCLUDE, ValidationError, fields, post_load, validate

from starknet_py.abi.v0.schemas import ContractAbiEntrySchema
from starknet_py.net.client_models import (
    CasmClass,
    CasmClassEntryPoint,
    CasmClassEntryPointsByType,
    DeployedContract,
    DeprecatedCompiledContract,
    DeprecatedContractClass,
    EntryPoint,
    EntryPointsByType,
    SierraCompiledContract,
    SierraContractClass,
    SierraEntryPoint,
    SierraEntryPointsByType,
    SyncStatus,
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


class AssertCurrentAccessIndicesIsEmpty(Enum):
    ASSERT_CURRENT_ACCESS_INDICES_IS_EMPTY = "AssertCurrentAccessIndicesIsEmpty"


class AssertAllKeysUsed(Enum):
    ASSERT_ALL_KEYS_USED = "AssertAllKeysUsed"


class AssertLeAssertThirdArcExcluded(Enum):
    ASSERT_LE_ASSERT_THIRD_ARC_EXCLUDED = "AssertLeAssertThirdArcExcluded"


class AssertAllAccessesUsedInnerSchema(Schema):
    n_used_accesses = fields.Nested(CellRefSchema(), required=True)


class AssertAllAccessesUsedSchema(Schema):
    assert_all_accesses_used = fields.Nested(
        AssertAllAccessesUsedInnerSchema(),
        data_key="AssertAllAccessesUsed",
        required=True,
    )


class DerefSchema(Schema):
    deref = fields.Nested(CellRefSchema(), data_key="Deref", required=True)


class DoubleDerefItemField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict):
            return CellRefSchema().load(value)
        elif isinstance(value, int):
            return value
        else:
            raise ValidationError(
                "Invalid value: must be a CellRef object or an integer"
            )

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, dict):
            return CellRefSchema().dump(value)
        elif isinstance(value, int):
            return value
        raise ValidationError("Invalid value type during serialization")


class DoubleDerefSchema(Schema):
    double_deref = fields.List(
        DoubleDerefItemField(),
        data_key="DoubleDeref",
        required=True,
        validate=validate.Length(2),
    )


class ImmediateSchema(Schema):
    immediate = NumberAsHex(data_key="Immediate", required=True)


class BinOpBField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return DerefSchema().load(value)
        except ValidationError as _e:
            pass
        try:
            return ImmediateSchema().load(value)
        except ValidationError as _e:
            pass

        raise ValidationError(
            f"Invalid value provided for 'b': {value}. Must be a Deref object or an Immediate object."
        )


class BinOpInnerSchema(Schema):
    op = fields.String(
        data_key="op", required=True, validate=validate.OneOf(["Add", "Mul"])
    )
    a = fields.Nested(CellRefSchema(), data_key="a", required=True)
    b = BinOpBField(data_key="b", required=True)


class BinOpSchema(Schema):
    bin_op = fields.Nested(BinOpInnerSchema(), data_key="BinOp", required=True)


class ResOperandField(fields.Field):
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


class AssertLtAssertValidInputSchema(Schema):
    assert_lt_assert_valid_input = fields.Nested(
        AssertLtAssertValidInputInnerSchema(),
        data_key="AssertLtAssertValidInput",
        required=True,
    )


class Felt252DictReadInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    key = ResOperandField(data_key="key", required=True)
    value_dst = fields.Nested(CellRefSchema(), data_key="value_dst", required=True)


class Felt252DictReadSchema(Schema):
    felt252_dict_read = fields.Nested(
        Felt252DictReadInnerSchema(), data_key="Felt252DictRead", required=True
    )


class Felt252DictWriteInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    key = ResOperandField(data_key="key", required=True)
    value = ResOperandField(data_key="value", required=True)


class Felt252DictWriteSchema(Schema):
    felt252_dict_write = fields.Nested(
        Felt252DictWriteInnerSchema(), data_key="Felt252DictWrite", required=True
    )


class AllocSegmentInnerSchema(Schema):
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)


class AllocSegmentSchema(Schema):
    alloc_segment = fields.Nested(
        AllocSegmentInnerSchema(), data_key="AllocSegment", required=True
    )


class TestLessThanInnerSchema(Schema):
    lhs = ResOperandField(data_key="lhs", required=True)
    rhs = ResOperandField(data_key="rhs", required=True)
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)


class TestLessThanSchema(Schema):
    test_less_than = fields.Nested(
        TestLessThanInnerSchema(), data_key="TestLessThan", required=True
    )


class TestLessThanOrEqualInnerSchema(TestLessThanInnerSchema):
    pass


class TestLessThanOrEqualSchema(Schema):
    test_less_than_or_equal = fields.Nested(
        TestLessThanOrEqualInnerSchema(), data_key="TestLessThanOrEqual", required=True
    )


class TestLessThenOrEqualAddressInnerSchema(TestLessThanSchema):
    pass


class TestLessThenOrEqualAddressSchema(Schema):
    test_less_than_or_equal_address = fields.Nested(
        TestLessThenOrEqualAddressInnerSchema(),
        data_key="TestLessThenOrEqualAddress",
        required=True,
    )


class WideMul128InnerSchema(Schema):
    lhs = ResOperandField(data_key="lhs", required=True)
    rhs = ResOperandField(data_key="rhs", required=True)
    high = fields.Nested(CellRefSchema(), data_key="high", required=True)
    low = fields.Nested(CellRefSchema(), data_key="low", required=True)


class WideMul128Schema(Schema):
    wide_mul128 = fields.Nested(
        WideMul128InnerSchema(), data_key="WideMul128", required=True
    )


class DivModInnerSchema(Schema):
    lhs = ResOperandField(data_key="lhs", required=True)
    rhs = ResOperandField(data_key="rhs", required=True)
    quotient = fields.Nested(CellRefSchema(), data_key="quotient", required=True)
    remainder = fields.Nested(CellRefSchema(), data_key="remainder", required=True)


class DivModSchema(Schema):
    div_mod = fields.Nested(DivModInnerSchema(), data_key="DivMod", required=True)


class Uint256DivModInnerSchema(Schema):
    dividend_0 = ResOperandField(data_key="dividend0", required=True)
    dividend_1 = ResOperandField(data_key="dividend1", required=True)
    divisor_0 = ResOperandField(data_key="divisor0", required=True)
    divisor_1 = ResOperandField(data_key="divisor1", required=True)
    quotient_0 = fields.Nested(CellRefSchema(), data_key="quotient0", required=True)
    quotient_1 = fields.Nested(CellRefSchema(), data_key="quotient1", required=True)
    remainder_0 = fields.Nested(CellRefSchema(), data_key="remainder0", required=True)
    remainder_1 = fields.Nested(CellRefSchema(), data_key="remainder1", required=True)


class Uint256DivModSchema(Schema):
    uint256_div_mod = fields.Nested(
        Uint256DivModInnerSchema(), data_key="Uint256DivMod", required=True
    )


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


class Uint512DivModByUint256Schema(Schema):
    uint512_div_mod_by_uint256 = fields.Nested(
        Uint512DivModByUint256InnerSchema(),
        data_key="Uint512DivModByUint256",
        required=True,
    )


class SquareRootInnerSchema(Schema):
    value = ResOperandField(data_key="value", required=True)
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)


class SquareRootSchema(Schema):
    square_root = fields.Nested(
        SquareRootInnerSchema(), data_key="SquareRoot", required=True
    )


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


class Uint256SquareRootSchema(Schema):
    uint256_square_root = fields.Nested(
        Uint256SquareRootInnerSchema(), data_key="Uint256SquareRoot", required=True
    )


class LinearSplitInnerSchema(Schema):
    value = ResOperandField(data_key="value", required=True)
    scalar = ResOperandField(data_key="scalar", required=True)
    max_x = ResOperandField(data_key="max_x", required=True)
    x = fields.Nested(CellRefSchema(), data_key="x", required=True)
    y = fields.Nested(CellRefSchema(), data_key="y", required=True)


class LinearSplitSchema(Schema):
    linear_split = fields.Nested(
        LinearSplitInnerSchema(), data_key="LinearSplit", required=True
    )


class AllocFelt252DictInnerSchema(Schema):
    segment_arena_ptr = ResOperandField(data_key="segment_arena_ptr", required=True)


class AllocFelt252DictSchema(Schema):
    alloc_felt252_dict = fields.Nested(
        AllocFelt252DictInnerSchema(), data_key="AllocFelt252Dict", required=True
    )


class Felt252DictEntryInitInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    key = ResOperandField(data_key="key", required=True)


class Felt252DictEntryInitSchema(Schema):
    felt252_dict_entry_init = fields.Nested(
        Felt252DictEntryInitInnerSchema(),
        data_key="Felt252DictEntryInit",
        required=True,
    )


class Felt252DictEntryUpdateInnerSchema(Schema):
    dict_ptr = ResOperandField(data_key="dict_ptr", required=True)
    value = ResOperandField(data_key="value", required=True)


class Felt252DictEntryUpdateSchema(Schema):
    felt252_dict_entry_update = fields.Nested(
        Felt252DictEntryUpdateInnerSchema(),
        data_key="Felt252DictEntryUpdate",
        required=True,
    )


class GetSegmentArenaIndexInnerSchema(Schema):
    dict_end_ptr = ResOperandField(data_key="dict_end_ptr", required=True)
    dict_index = ResOperandField(data_key="dict_index", required=True)


class GetSegmentArenaIndexSchema(Schema):
    get_segment_arena_index = fields.Nested(
        GetSegmentArenaIndexInnerSchema(),
        data_key="GetSegmentArenaIndex",
        required=True,
    )


class InitSquashDataInnerSchema(Schema):
    dict_access = ResOperandField(data_key="dict_access", required=True)
    ptr_diff = ResOperandField(data_key="ptr_diff", required=True)
    n_accesses = ResOperandField(data_key="n_accesses", required=True)
    big_keys = fields.Nested(CellRefSchema(), data_key="big_keys", required=True)
    first_key = fields.Nested(CellRefSchema(), data_key="first_key", required=True)


class InitSquashDataSchema(Schema):
    init_squash_data = fields.Nested(
        InitSquashDataInnerSchema(), data_key="InitSquashData", required=True
    )


class GetCurrentAccessIndexInnerSchema(Schema):
    range_check_ptr = ResOperandField(data_key="range_check_ptr", required=True)


class GetCurrentAccessIndexSchema(Schema):
    get_current_access_index = fields.Nested(
        GetCurrentAccessIndexInnerSchema(),
        data_key="GetCurrentAccessIndex",
        required=True,
    )


class ShouldSkipSquashLoopInnerSchema(Schema):
    should_skip_loop = fields.Nested(
        CellRefSchema(), data_key="should_skip_loop", required=True
    )


class ShouldSkipSquashLoopSchema(Schema):
    should_skip_squash_loop = fields.Nested(
        ShouldSkipSquashLoopInnerSchema(),
        data_key="ShouldSkipSquashLoop",
        required=True,
    )


class GetCurrentAccessDeltaInnerSchema(Schema):
    index_delta_minus_1 = fields.Nested(
        CellRefSchema(), data_key="index_delta_minus1", required=True
    )


class GetCurrentAccessDeltaSchema(Schema):
    get_current_access_delta = fields.Nested(
        GetCurrentAccessDeltaInnerSchema(),
        data_key="GetCurrentAccessDelta",
        required=True,
    )


class ShouldContinueSquashLoopInnerSchema(Schema):
    should_continue = fields.Nested(
        CellRefSchema(), data_key="should_continue", required=True
    )


class ShouldContinueSquashLoopSchema(Schema):
    should_continue_squash_loop = fields.Nested(
        ShouldContinueSquashLoopInnerSchema(),
        data_key="ShouldContinueSquashLoop",
        required=True,
    )


class GetNextDictKeyInnerSchema(Schema):
    next_key = fields.Nested(CellRefSchema(), data_key="next_key", required=True)


class GetNextDictKeySchema(Schema):
    get_next_dict_key = fields.Nested(
        GetNextDictKeyInnerSchema(), data_key="GetNextDictKey", required=True
    )


class AssertLeFindSmallArcsInnerSchema(Schema):
    range_check_ptr = ResOperandField(data_key="range_check_ptr", required=True)
    a = ResOperandField(data_key="a", required=True)
    b = ResOperandField(data_key="b", required=True)


class AssertLeFindSmallArcsSchema(Schema):
    assert_le_find_small_arcs = fields.Nested(
        AssertLeFindSmallArcsInnerSchema(),
        data_key="AssertLeFindSmallArcs",
        required=True,
    )


class AssertLeIsFirstArcExcludedInnerSchema(Schema):
    skip_exclude_a_flag = fields.Nested(
        CellRefSchema(), data_key="skip_exclude_a_flag", required=True
    )


class AssertLeIsFirstArcExcludedSchema(Schema):
    assert_le_is_first_arc_excluded = fields.Nested(
        AssertLeIsFirstArcExcludedInnerSchema(),
        data_key="AssertLeIsFirstArcExcluded",
        required=True,
    )


class AssertLeIsSecondArcExcludedInnerSchema(Schema):
    skip_exclude_b_minus_a = fields.Nested(
        CellRefSchema(), data_key="skip_exclude_b_minus_a", required=True
    )


class AssertLeIsSecondArcExcludedSchema(Schema):
    assert_le_is_second_arc_excluded = fields.Nested(
        AssertLeIsSecondArcExcludedInnerSchema(),
        data_key="AssertLeIsSecondArcExcluded",
        required=True,
    )


class RandomEcPointInnerSchema(Schema):
    x = fields.Nested(CellRefSchema(), data_key="x", required=True)
    y = fields.Nested(CellRefSchema(), data_key="y", required=True)


class RandomEcPointSchema(Schema):
    random_ec_point = fields.Nested(
        RandomEcPointInnerSchema(), data_key="RandomEcPoint", required=True
    )


class FieldSqrtInnerSchema(Schema):
    val = ResOperandField(data_key="val", required=True)
    sqrt = fields.Nested(CellRefSchema(), data_key="sqrt", required=True)


class FieldSqrtSchema(Schema):
    field_sqrt = fields.Nested(
        FieldSqrtInnerSchema(), data_key="FieldSqrt", required=True
    )


class DebugPrintInnerSchema(Schema):
    start = ResOperandField(data_key="start", required=True)
    end = ResOperandField(data_key="end", required=True)


class DebugPrintSchema(Schema):
    debug_print = fields.Nested(
        DebugPrintInnerSchema(), data_key="DebugPrint", required=True
    )


class AllocConstantSizeInnerSchema(Schema):
    size = ResOperandField(data_key="size", required=True)
    dst = fields.Nested(CellRefSchema(), data_key="dst", required=True)


class AllocConstantSizeSchema(Schema):
    alloc_constant_size = fields.Nested(
        AllocConstantSizeInnerSchema(), data_key="AllocConstantSize", required=True
    )


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


class U256InvModNSchema(Schema):
    u256_inv_mod_n = fields.Nested(
        U256InvModNInnerSchema(), data_key="U256InvModN", required=True
    )


class EvalCircuitInnerSchema(Schema):
    n_add_mods = ResOperandField(data_key="n_add_mods", required=True)
    add_mod_builtin = ResOperandField(data_key="add_mod_builtin", required=True)
    n_mul_mods = ResOperandField(data_key="n_mul_mods", required=True)
    mul_mod_builtin = ResOperandField(data_key="mul_mod_builtin", required=True)


class EvalCircuitSchema(Schema):
    eval_circuit = fields.Nested(
        EvalCircuitInnerSchema(), data_key="EvalCircuit", required=True
    )


class SystemCallInnerSchema(Schema):
    system = ResOperandField(data_key="system", required=True)


class SystemCallSchema(Schema):
    system_call = fields.Nested(
        SystemCallInnerSchema(), data_key="SystemCall", required=True
    )


class CheatcodeInnerSchema(Schema):
    selector = NumberAsHex(
        data_key="selector", required=True
    )  # Assuming NUM_AS_HEX is represented as a string
    input_start = ResOperandField(data_key="input_start", required=True)
    input_end = ResOperandField(data_key="input_end", required=True)
    output_start = fields.Nested(
        CellRefSchema(), data_key="output_start", required=True
    )
    output_end = fields.Nested(CellRefSchema(), data_key="output_end", required=True)


class CheatcodeSchema(Schema):
    cheatcode = fields.Nested(
        CheatcodeInnerSchema(), data_key="Cheatcode", required=True
    )


class HintField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            # Deprecated hint checks
            if value in AssertCurrentAccessIndicesIsEmpty:
                return value
            elif value in AssertAllKeysUsed:
                return value
            elif value in AssertLeAssertThirdArcExcluded:
                return value

        elif isinstance(value, dict):
            # Deprecated hint
            if AssertAllAccessesUsedSchema.assert_all_accesses_used.data_key in value:
                return AssertAllAccessesUsedSchema().load(value)
            elif (
                AssertLtAssertValidInputSchema.assert_lt_assert_valid_input.data_key
                in value
            ):
                return AssertLtAssertValidInputSchema().load(value)
            elif Felt252DictReadSchema.felt252_dict_read.data_key in value:
                return Felt252DictReadSchema().load(value)
            elif Felt252DictWriteSchema.felt252_dict_write.data_key in value:
                return Felt252DictWriteSchema().load(value)

            # Core hint
            elif AllocSegmentSchema.alloc_segment.data_key in value:
                return AllocSegmentSchema().load(value)
            elif TestLessThanSchema.test_less_than.data_key in value:
                return TestLessThanSchema().load(value)
            elif TestLessThanOrEqualSchema.test_less_than_or_equal.data_key in value:
                return TestLessThanOrEqualSchema().load(value)
            elif (
                TestLessThenOrEqualAddressSchema.test_less_than_or_equal_address.data_key
                in value
            ):
                return TestLessThenOrEqualAddressSchema().load(value)
            elif WideMul128Schema.wide_mul128.data_key in value:
                return WideMul128Schema().load(value)
            elif DivModSchema.div_mod.data_key in value:
                return DivModSchema().load(value)
            elif Uint256DivModSchema.uint256_div_mod.data_key in value:
                return Uint256DivModSchema().load(value)
            elif (
                Uint512DivModByUint256Schema.uint512_div_mod_by_uint256.data_key
                in value
            ):
                return Uint512DivModByUint256Schema().load(value)
            elif SquareRootSchema.square_root.data_key in value:
                return SquareRootSchema().load(value)
            elif Uint256SquareRootSchema.uint256_square_root.data_key in value:
                return Uint256SquareRootSchema().load(value)
            elif LinearSplitSchema.linear_split.data_key in value:
                return LinearSplitSchema().load(value)
            elif AllocFelt252DictSchema.alloc_felt252_dict.data_key in value:
                return AllocFelt252DictSchema().load(value)
            elif Felt252DictEntryInitSchema.felt252_dict_entry_init.data_key in value:
                return Felt252DictEntryInitSchema().load(value)
            elif (
                Felt252DictEntryUpdateSchema.felt252_dict_entry_update.data_key in value
            ):
                return Felt252DictEntryUpdateSchema().load(value)
            elif GetSegmentArenaIndexSchema.get_segment_arena_index.data_key in value:
                return GetSegmentArenaIndexSchema().load(value)
            elif InitSquashDataSchema.init_squash_data.data_key in value:
                return InitSquashDataSchema().load(value)
            elif GetCurrentAccessIndexSchema.get_current_access_index.data_key in value:
                return GetCurrentAccessIndexSchema().load(value)
            elif ShouldSkipSquashLoopSchema.should_skip_squash_loop.data_key in value:
                return ShouldSkipSquashLoopSchema().load(value)
            elif GetCurrentAccessDeltaSchema.get_current_access_delta.data_key in value:
                return GetCurrentAccessDeltaSchema().load(value)
            elif (
                ShouldContinueSquashLoopSchema.should_continue_squash_loop.data_key
                in value
            ):
                return ShouldContinueSquashLoopSchema().load(value)
            elif GetNextDictKeySchema.get_next_dict_key.data_key in value:
                return GetNextDictKeySchema().load(value)
            elif (
                AssertLeFindSmallArcsSchema.assert_le_find_small_arcs.data_key in value
            ):
                return AssertLeFindSmallArcsSchema().load(value)
            elif (
                AssertLeIsFirstArcExcludedSchema.assert_le_is_first_arc_excluded.data_key
                in value
            ):
                return AssertLeIsFirstArcExcludedSchema().load(value)
            elif (
                AssertLeIsSecondArcExcludedSchema.assert_le_is_second_arc_excluded.data_key
                in value
            ):
                return AssertLeIsSecondArcExcludedSchema().load(value)
            elif RandomEcPointSchema.random_ec_point.data_key in value:
                return RandomEcPointSchema().load(value)
            elif FieldSqrtSchema.field_sqrt.data_key in value:
                return FieldSqrtSchema().load(value)
            elif DebugPrintSchema.debug_print.data_key in value:
                return DebugPrintSchema().load(value)
            elif AllocConstantSizeSchema.alloc_constant_size.data_key in value:
                return AllocConstantSizeSchema().load(value)
            elif U256InvModNSchema.u256_inv_mod_n.data_key in value:
                return U256InvModNSchema().load(value)
            elif EvalCircuitSchema.eval_circuit.data_key in value:
                return EvalCircuitSchema().load(value)

            # Starknet hint
            elif SystemCallSchema.system_call.data_key in value:
                return SystemCallSchema().load(value)
            elif CheatcodeSchema.cheatcode.data_key in value:
                return CheatcodeSchema().load(value)


class CasmClassSchema(Schema):
    prime = NumberAsHex(data_key="prime", required=True)
    bytecode = fields.List(Felt(), data_key="bytecode", required=True)
    bytecode_segment_lengths = fields.List(
        fields.Integer(), data_key="bytecode_segment_lengths", load_default=None
    )
    # TODO (#1498): Add more detailed `hints` type
    hints = fields.List(
        fields.List(
            HintField(),
            validate=validate.Length(equal=2),
        ),
        data_key="hints",
        required=True,
    )
    # TODO (#1498): Ensure `pythonic_hints` are not needed anymore
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
