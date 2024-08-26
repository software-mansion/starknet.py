//! L1 L2 messaging demo contract.
//! Rewrite in Cairo 1 of the contract from previous Devnet version:
//! https://github.com/0xSpaceShard/starknet-devnet/blob/e477aa1bbe2348ba92af2a69c32d2eef2579d863/test/contracts/cairo/l1l2.cairo
//!
//! This contract does not use interface to keep the code as simple as possible.
//!

#[starknet::contract]
mod l1_l2 {
    const MESSAGE_WITHDRAW: felt252 = 0;

    #[storage]
    struct Storage {
        // Balances (users) -> (amount).
        balances: LegacyMap<felt252, felt252>,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        DepositFromL1: DepositFromL1,
    }

    #[derive(Drop, starknet::Event)]
    struct DepositFromL1 {
        #[key]
        user: felt252,
        #[key]
        amount: felt252,
    }

    /// Gets the balance of the `user`.
    #[external(v0)]
    fn get_balance(self: @ContractState, user: felt252) -> felt252 {
        self.balances.read(user)
    }

    /// Increases the balance of the `user` for the `amount`.
    #[external(v0)]
    fn increase_balance(ref self: ContractState, user: felt252, amount: felt252) {
        let balance = self.balances.read(user);
        self.balances.write(user, balance + amount);
    }

    /// Withdraws the `amount` for the `user` and sends a message to `l1_address` to
    /// send the funds.
    #[external(v0)]
    fn withdraw(ref self: ContractState, user: felt252, amount: felt252, l1_address: felt252) {
        assert(amount.is_non_zero(), 'Amount must be positive');

        let balance = self.balances.read(user);
        assert(balance.is_non_zero(), 'Balance is already 0');

        // We need u256 to make comparisons.
        let balance_u: u256 = balance.into();
        let amount_u: u256 = amount.into();
        assert(balance_u >= amount_u, 'Balance will be negative');

        let new_balance = balance - amount;

        self.balances.write(user, new_balance);

        let payload = array![MESSAGE_WITHDRAW, user, amount,];

        starknet::send_message_to_l1_syscall(l1_address, payload.span()).unwrap();
    }

    /// Withdraws the `amount` for the `user` and sends a message to `l1_address` to
    /// send the funds.
    #[external(v0)]
    fn withdraw_from_lib(
        ref self: ContractState, user: felt252, amount: felt252, l1_address: felt252, message_sender_class_hash: starknet::ClassHash,
    ) {
        assert(amount.is_non_zero(), 'Amount must be positive');

        let balance = self.balances.read(user);
        assert(balance.is_non_zero(), 'Balance is already 0');

        // We need u256 to make comparisons.
        let balance_u: u256 = balance.into();
        let amount_u: u256 = amount.into();
        assert(balance_u >= amount_u, 'Balance will be negative');

        let new_balance = balance - amount;

        self.balances.write(user, new_balance);

        let calldata = array![user, amount, l1_address];

        starknet::SyscallResultTrait::unwrap_syscall(
            starknet::library_call_syscall(
                message_sender_class_hash,
                selector!("send_withdraw_message"),
                calldata.span(),
            )
        );
    }

    /// Deposits the `amount` for the `user`. Can only be called by the sequencer itself,
    /// after having fetched some messages from the L1.
    #[l1_handler]
    fn deposit(ref self: ContractState, from_address: felt252, user: felt252, amount: felt252) {
        // In a real case scenario, here we would assert from_address value

        let balance = self.balances.read(user);
        self.balances.write(user, balance + amount);

        self.emit(DepositFromL1 { user, amount });
    }
}
