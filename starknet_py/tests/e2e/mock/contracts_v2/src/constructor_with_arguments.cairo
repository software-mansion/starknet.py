#[derive(Clone, Debug, PartialEq, Drop, Serde, starknet::Store)]
pub struct NestedStruct {
    pub value: felt252,
}

#[derive(Clone, Debug, PartialEq, Drop, Serde, starknet::Store)]
pub struct TopStruct {
    pub value: felt252,
    pub nested_struct: NestedStruct,
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

    #[external(v0)]
    fn get(self: @ContractState) -> (felt252, (felt252, (felt252, felt252)), felt252, TopStruct) {
        let single_value = self.single_value.read();
        let tuple = self.tuple.read();
        let arr_sum = self.arr_sum.read();
        let dict = self.dict.read();

        (single_value, tuple, arr_sum, dict)
    }
}