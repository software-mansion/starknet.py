#[starknet::interface]
trait ISimpleStorageWithEvent<TContractState> {
    fn put(ref self: TContractState, key: felt252, value: felt252);
    fn another_put(ref self: TContractState, key: felt252, value: felt252);
}

#[derive(Drop, Clone, starknet::Event)]
struct PutCalled {
    key: felt252,
    prev_value: felt252,
    value: felt252,
}

#[derive(Drop, Clone, starknet::Event)]
struct AnotherPutCalled {
    key: felt252,
    prev_value: felt252,
    value: felt252,
    additional_value: felt252,
}

#[starknet::contract]
pub mod SimpleStorageWithEvent {
    use super::{PutCalled, AnotherPutCalled};

    #[storage]
    struct Storage {
        map: LegacyMap::<felt252, felt252>,
    }

    #[event]
    #[derive(Drop, Clone, starknet::Event)]
    pub enum Event {
        PutCalled: PutCalled,
        AnotherPutCalled: AnotherPutCalled,
    }

    #[abi(embed_v0)]
    impl SimpleStorag of super::ISimpleStorageWithEvent<ContractState> {
        fn put(ref self: ContractState, key: felt252, value: felt252) {
            let mut prev_value = self.map.read(key);
            self.map.write(key, value);
            self.emit(PutCalled { key: key, prev_value: prev_value, value: value });
        }

        fn another_put(ref self: ContractState, key: felt252, value: felt252) {
            let mut prev_value = self.map.read(key);
            self.map.write(key, value);
            self
                .emit(
                    AnotherPutCalled {
                        key: key, prev_value: prev_value, value: value, additional_value: value,
                    },
                );
        }
    }
}
