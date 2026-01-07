#[starknet::contract]
mod SaltedContract {
    #[storage]
    struct Storage {}
    #[external(v0)]
    fn empty_(ref self: ContractState) {}
}
