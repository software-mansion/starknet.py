

#[contract]
mod SimpleStorageWithEvent {

    struct Storage {
        map: LegacyMap::<felt252, felt252>,
    }

    #[event]
    fn PutCalled (
        key: felt252,
        prev_value: felt252,
        value: felt252,
    ){}

    #[event]
    fn AnotherPutCalled(
        key: felt252,
        prev_value: felt252,
        value: felt252,
        additional_value: felt252,
    ){}

    #[external]
    fn put(key: felt252, value: felt252) {
        let mut prev_value = map::read(key);
        map::write(key, value);
        PutCalled(key, prev_value, value);
    }

    #[external]
    fn another_put(key: felt252, value: felt252) {
        let mut prev_value = map::read(key);
        map::write(key, value);
        AnotherPutCalled(key, prev_value, value, value);
    }

}