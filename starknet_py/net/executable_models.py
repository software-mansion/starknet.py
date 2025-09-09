from dataclasses import dataclass
from enum import Enum
from typing import List, Literal, Optional, Tuple, Union

from starknet_py.net.client_models import CasmClassEntryPointsByType


class AssertCurrentAccessIndicesIsEmpty(Enum):
    ASSERT_CURRENT_ACCESS_INDICES_IS_EMPTY = "AssertCurrentAccessIndicesIsEmpty"


class AssertAllKeysUsed(Enum):
    ASSERT_ALL_KEYS_USED = "AssertAllKeysUsed"


class AssertLeAssertThirdArcExcluded(Enum):
    ASSERT_LE_ASSERT_THIRD_ARC_EXCLUDED = "AssertLeAssertThirdArcExcluded"


@dataclass
class CellRef:
    register: Literal["AP", "FP"]
    offset: int


@dataclass
class AssertAllAccessesUsedInner:
    n_used_accesses: CellRef


@dataclass
class AssertAllAccessesUsed:
    assert_all_accesses_used: AssertAllAccessesUsedInner


@dataclass
class Deref:
    deref: CellRef


@dataclass
class DoubleDeref:
    double_deref: Tuple[CellRef, int]


@dataclass
class Immediate:
    immediate: int


@dataclass
class BinOpInner:
    op: Literal["Add", "Mul"]
    a: CellRef
    b: Union[Deref, Immediate]


@dataclass
class BinOp:
    bin_op: BinOpInner


ResOperand = Union[Deref, DoubleDeref, Immediate, BinOp]


@dataclass
class AssertLtAssertValidInputInner:
    a: ResOperand
    b: ResOperand


@dataclass
class AssertLtAssertValidInput:
    assert_lt_assert_valid_input: AssertLtAssertValidInputInner


@dataclass
class Felt252DictReadInner:
    dict_ptr: ResOperand
    key: ResOperand
    value_dst: CellRef


@dataclass
class Felt252DictRead:
    felt252_dict_read: Felt252DictReadInner


@dataclass
class Felt252DictWriteInner:
    dict_ptr: ResOperand
    key: ResOperand
    value: ResOperand


@dataclass
class Felt252DictWrite:
    felt252_dict_write: Felt252DictWriteInner


@dataclass
class AllocSegmentInner:
    dst: CellRef


@dataclass
class AllocSegment:
    alloc_segment: AllocSegmentInner


@dataclass
class TestLessThanInner:
    lhs: ResOperand
    rhs: ResOperand
    dst: CellRef


@dataclass
class TestLessThan:
    test_less_than: TestLessThanInner


@dataclass
class TestLessThanOrEqualInner(TestLessThanInner):
    pass


@dataclass
class TestLessThanOrEqual:
    test_less_than_or_equal: TestLessThanOrEqualInner


@dataclass
class TestLessThanOrEqualAddressInner(TestLessThanInner):
    pass


@dataclass
class TestLessThanOrEqualAddress:
    test_less_than_or_equal_address: TestLessThanOrEqualAddressInner


@dataclass
class WideMul128Inner:
    lhs: ResOperand
    rhs: ResOperand
    high: CellRef
    low: CellRef


@dataclass
class WideMul128:
    wide_mul128: WideMul128Inner


@dataclass
class DivModInner:
    lhs: ResOperand
    rhs: ResOperand
    quotient: CellRef
    remainder: CellRef


@dataclass
class DivMod:
    div_mod: DivModInner


@dataclass
class Uint256DivModInner:
    # pylint: disable=too-many-instance-attributes
    dividend0: ResOperand
    dividend1: ResOperand
    divisor0: ResOperand
    divisor1: ResOperand
    quotient0: CellRef
    quotient1: CellRef
    remainder0: CellRef
    remainder1: CellRef


@dataclass
class Uint256DivMod:
    uint256_div_mod: Uint256DivModInner


@dataclass
class Uint512DivModByUint256Inner:
    # pylint: disable=too-many-instance-attributes
    dividend0: ResOperand
    dividend1: ResOperand
    dividend2: ResOperand
    dividend3: ResOperand
    divisor0: ResOperand
    divisor1: ResOperand
    quotient0: CellRef
    quotient1: CellRef
    quotient2: CellRef
    quotient3: CellRef
    remainder0: CellRef
    remainder1: CellRef


@dataclass
class Uint512DivModByUint256:
    uint512_div_mod_by_uint256: Uint512DivModByUint256Inner


@dataclass
class SquareRootInner:
    value: ResOperand
    dst: CellRef


@dataclass
class SquareRoot:
    square_root: SquareRootInner


@dataclass
class Uint256SquareRootInner:
    value_low: ResOperand
    value_high: ResOperand
    sqrt0: CellRef
    sqrt1: CellRef
    remainder_low: CellRef
    remainder_high: CellRef
    sqrt_mul_2_minus_remainder_ge_u128: CellRef


@dataclass
class Uint256SquareRoot:
    uint256_square_root: Uint256SquareRootInner


@dataclass
class LinearSplitInner:
    value: ResOperand
    scalar: ResOperand
    max_x: ResOperand
    x: CellRef
    y: CellRef


@dataclass
class LinearSplit:
    linear_split: LinearSplitInner


@dataclass
class AllocFelt252DictInner:
    segment_arena_ptr: ResOperand


@dataclass
class AllocFelt252Dict:
    alloc_felt252_dict: AllocFelt252DictInner


@dataclass
class Felt252DictEntryInitInner:
    dict_ptr: ResOperand
    key: ResOperand


@dataclass
class Felt252DictEntryInit:
    felt252_dict_entry_init: Felt252DictEntryInitInner


@dataclass
class Felt252DictEntryUpdateInner:
    dict_ptr: ResOperand
    value: ResOperand


@dataclass
class Felt252DictEntryUpdate:
    felt252_dict_entry_update: Felt252DictEntryUpdateInner


@dataclass
class GetSegmentArenaIndexInner:
    dict_end_ptr: ResOperand
    dict_index: CellRef


@dataclass
class GetSegmentArenaIndex:
    get_segment_arena_index: GetSegmentArenaIndexInner


@dataclass
class InitSquashDataInner:
    dict_accesses: ResOperand
    ptr_diff: ResOperand
    n_accesses: ResOperand
    big_keys: CellRef
    first_key: CellRef


@dataclass
class InitSquashData:
    init_squash_data: InitSquashDataInner


@dataclass
class GetCurrentAccessIndexInner:
    range_check_ptr: ResOperand


@dataclass
class GetCurrentAccessIndex:
    get_current_access_index: GetCurrentAccessIndexInner


@dataclass
class ShouldSkipSquashLoopInner:
    should_skip_loop: CellRef


@dataclass
class ShouldSkipSquashLoop:
    should_skip_squash_loop: ShouldSkipSquashLoopInner


@dataclass
class GetCurrentAccessDeltaInner:
    index_delta_minus1: CellRef


@dataclass
class GetCurrentAccessDelta:
    get_current_access_delta: GetCurrentAccessDeltaInner


@dataclass
class ShouldContinueSquashLoopInner:
    should_continue: CellRef


@dataclass
class ShouldContinueSquashLoop:
    should_continue_squash_loop: ShouldContinueSquashLoopInner


@dataclass
class GetNextDictKeyInner:
    next_key: CellRef


@dataclass
class GetNextDictKey:
    get_next_dict_key: GetNextDictKeyInner


@dataclass
class AssertLeFindSmallArcsInner:
    range_check_ptr: ResOperand
    a: ResOperand
    b: ResOperand


@dataclass
class AssertLeFindSmallArcs:
    assert_le_find_small_arcs: AssertLeFindSmallArcsInner


@dataclass
class AssertLeIsFirstArcExcludedInner:
    skip_exclude_a_flag: CellRef


@dataclass
class AssertLeIsFirstArcExcluded:
    assert_le_is_first_arc_excluded: AssertLeIsFirstArcExcludedInner


@dataclass
class AssertLeIsSecondArcExcludedInner:
    skip_exclude_b_minus_a: CellRef


@dataclass
class AssertLeIsSecondArcExcluded:
    assert_le_is_second_arc_excluded: AssertLeIsSecondArcExcludedInner


@dataclass
class RandomEcPointInner:
    x: CellRef
    y: CellRef


@dataclass
class RandomEcPoint:
    random_ec_point: RandomEcPointInner


@dataclass
class FieldSqrtInner:
    val: ResOperand
    sqrt: CellRef


@dataclass
class FieldSqrt:
    field_sqrt: FieldSqrtInner


@dataclass
class DebugPrintInner:
    start: ResOperand
    end: ResOperand


@dataclass
class DebugPrint:
    debug_print: DebugPrintInner


@dataclass
class AllocConstantSizeInner:
    size: ResOperand
    dst: CellRef


@dataclass
class AllocConstantSize:
    alloc_constant_size: AllocConstantSizeInner


@dataclass
class U256InvModNInner:
    # pylint: disable=too-many-instance-attributes
    b0: ResOperand
    b1: ResOperand
    n0: ResOperand
    n1: ResOperand
    g0_or_no_inv: CellRef
    g1_option: CellRef
    s_or_r0: CellRef
    s_or_r1: CellRef
    t_or_k0: CellRef
    t_or_k1: CellRef


@dataclass
class U256InvModN:
    u256_inv_mod_n: U256InvModNInner


@dataclass
class EvalCircuitInner:
    n_add_mods: ResOperand
    add_mod_builtin: ResOperand
    n_mul_mods: ResOperand
    mul_mod_builtin: ResOperand


@dataclass
class EvalCircuit:
    eval_circuit: EvalCircuitInner


@dataclass
class SystemCallInner:
    system: ResOperand


@dataclass
class SystemCall:
    system_call: SystemCallInner


@dataclass
class CheatcodeInner:
    selector: int
    input_start: ResOperand
    input_end: ResOperand
    output_start: CellRef
    output_end: CellRef


@dataclass
class Cheatcode:
    cheatcode: CheatcodeInner


Hint = Union[
    AssertCurrentAccessIndicesIsEmpty,
    AssertAllKeysUsed,
    AssertLeAssertThirdArcExcluded,
    AssertAllAccessesUsed,
    AssertLtAssertValidInput,
    Felt252DictRead,
    Felt252DictWrite,
    AllocSegment,
    TestLessThan,
    TestLessThanOrEqual,
    TestLessThanOrEqualAddress,
    WideMul128,
    DivMod,
    Uint256DivMod,
    Uint512DivModByUint256,
    SquareRoot,
    Uint256SquareRoot,
    LinearSplit,
    AllocFelt252Dict,
    Felt252DictEntryInit,
    Felt252DictEntryUpdate,
    GetSegmentArenaIndex,
    InitSquashData,
    GetCurrentAccessIndex,
    ShouldSkipSquashLoop,
    GetCurrentAccessDelta,
    ShouldContinueSquashLoop,
    GetNextDictKey,
    AssertLeFindSmallArcs,
    AssertLeIsFirstArcExcluded,
    AssertLeIsSecondArcExcluded,
    RandomEcPoint,
    FieldSqrt,
    DebugPrint,
    AllocConstantSize,
    U256InvModN,
    EvalCircuit,
    SystemCall,
    Cheatcode,
]


@dataclass
class CasmClass:
    """
    Dataclass representing class compiled to Cairo assembly.
    """

    prime: int
    bytecode: List[int]
    hints: List[Tuple[int, List[Hint]]]
    compiler_version: str
    entry_points_by_type: CasmClassEntryPointsByType
    bytecode_segment_lengths: Optional[List[int]]
