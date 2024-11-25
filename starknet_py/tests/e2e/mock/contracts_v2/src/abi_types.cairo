use core::serde::Serde;
use starknet::ContractAddress;
use core::zeroable::NonZero;
use core::zeroable::IsZeroResult;
use core::zeroable::NonZeroIntoImpl;

#[derive(Drop, Serde)]
enum ExampleEnum {
    variant_a: felt252,
    variant_b: u256,
}

#[derive(Drop, Serde)]
struct ExampleStruct {
    field_a: felt252,
    field_b: felt252,
    field_c: ExampleEnum,
    field_d: (),
    field_e: NonZero<felt252>,
}

#[starknet::interface]
trait IAbiTest<TContractState> {
    fn example_view_function(self: @TContractState) -> ExampleEnum;
    fn example_external_function(
        ref self: TContractState, recipient: ContractAddress, amount: u256
    ) -> ExampleStruct;
}

pub fn felt_to_nonzero(value: felt252) -> NonZero<felt252> {
    match felt252_is_zero(value) {
        IsZeroResult::Zero(()) => panic(ArrayTrait::new()),
        IsZeroResult::NonZero(x) => x,
    }
}

#[starknet::contract]
mod AbiTypes {
    use core::array::ArrayTrait;
    use core::traits::Into;
    use starknet::ContractAddress;
    use super::{ExampleEnum, ExampleStruct, felt_to_nonzero};

    #[storage]
    struct Storage {}

    #[event]
    fn ExampleEvent(value_a: u256, value_b: ExampleStruct) {}

    #[abi(embed_v0)]
    impl AbiTest of super::IAbiTest<ContractState> {
        fn example_view_function(self: @ContractState) -> ExampleEnum {
            ExampleEnum::variant_a(100)
        }
        fn example_external_function(
            ref self: ContractState, recipient: ContractAddress, amount: u256
        ) -> ExampleStruct {
            ExampleStruct {
                field_a: 200,
                field_b: 300,
                field_c: ExampleEnum::variant_b(400.into()),
                field_d: (),
                field_e: felt_to_nonzero(100),
            }
        }
    }

    #[l1_handler]
    fn example_l1_handler(ref self: ContractState, from_address: felt252, arg1: felt252) {}
}
