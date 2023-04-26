use serde::Serde;
use array::SpanTrait;


#[contract]
mod HelloStarknet {
    use super::OptionStruct;
    struct Storage {
        balance: felt252,
    }

    // Increases the balance by the given amount.
    #[external]
    fn increase_balance(amount: felt252) {
        balance::write(balance::read() + amount);
    }

    // Returns the current balance.
    #[view]
    fn get_balance() -> OptionStruct {
        balance::read()
    }
}


struct OptionStruct {
    first_field: felt252,
    second_field: Option<u256>,
    third_field: u8
}

impl OptionStructSerde of Serde<OptionStruct> {
    fn serialize(ref output: Array<felt252>, input: OptionStruct) {
        let OptionStruct{first_field, second_field, third_field} = input;
        Serde::serialize(ref output, first_field);
        Serde::serialize(ref output, second_field);
        Serde::serialize(ref output, third_field);
    }

    fn deserialize(ref serialized: Span<felt252>) -> Option<OptionStruct> {
        let first_field = Serde::<felt252>::deserialize(ref serialized)?;
        let second_field = Serde::<Option<u256>>::deserialize(ref serialized)?;
        let third_field = Serde::<u8>::deserialize(ref serialized)?;

        Option::Some(OptionStruct { first_field, second_field, third_field })
    }
}
