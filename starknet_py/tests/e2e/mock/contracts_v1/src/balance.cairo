#[contract]
mod Balance {
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
    fn get_balance() -> felt252 {
        balance::read()
    }
    // This function was added because in this directory exists almost the same contract with the same name,
    // becaouse of that we need to add additonal function to differ classhash.
    #[view]
    fn get_balance2() -> felt252 {
        balance::read()
    }
}
