#[derive(Clone, Debug, PartialEq, Drop, Serde, starknet::Store)]
struct NestedStruct {
    value: felt252,
}

#[derive(Clone, Debug, PartialEq, Drop, Serde, starknet::Store)]
struct TopStruct {
    value: felt252,
    nested_struct: NestedStruct,
}

#[starknet::contract]
mod ConstructorWithArguments {
    use super::{TopStruct, NestedStruct};

    #[storage]
    struct Storage {
        single_value: felt252,
        tuple: (felt252, (felt252, felt252)),
        arr_sum: felt252,
        dict: TopStruct,
    }

    #[constructor]
    fn constructor(ref self: ContractState, single_value: felt252, tuple: (felt252, (felt252, felt252)), arr: Array<felt252>, dict: TopStruct) {
        let mut sum = 0;

        let count = arr.len();
        let mut i: usize = 0;

        while i != count {
            let element: felt252 = arr[i].clone();
            sum += element;
            i += 1;
        };

        self.single_value.write(single_value);
        self.tuple.write(tuple);
        self.arr_sum.write(sum);
        self.dict.write(dict);
    }
}