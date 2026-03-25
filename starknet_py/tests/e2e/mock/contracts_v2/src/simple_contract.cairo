#[starknet::contract]
mod SimpleContract {
    #[storage]
    struct Storage {}
    #[external(v0)]
    fn empty___salt_placeholder__(ref self: ContractState) {}
}
