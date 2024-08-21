#[contract]
mod Map {

    struct Storage {
        storage: LegacyMap::<felt252, felt252>,
    }

    #[external]
    fn put(key: felt252, value: felt252) {
        storage::write(key, value);
    }

    #[external]
    fn get(key: felt252) -> felt252 {
        storage::read(key)
    }

}
