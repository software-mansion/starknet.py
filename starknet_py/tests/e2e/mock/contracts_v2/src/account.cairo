#[starknet::contract]
mod Account {
    use array::ArrayTrait;
    use box::BoxTrait;
    use ecdsa::check_ecdsa_signature;
    use option::OptionTrait;
    use starknet::account::Call;
    use starknet::{ContractAddress, syscalls, SyscallResultTrait};
    use zeroable::Zeroable;
    #[storage]
    struct Storage {
        public_key: felt252
    }

    #[constructor]
    fn constructor(ref self: ContractState, public_key_: felt252) {
        self.public_key.write(public_key_);
    }

    trait StorageTrait {
        fn validate_transaction(self: @ContractState) -> felt252;
    }
    impl StorageImpl of StorageTrait {
        fn validate_transaction(self: @ContractState) -> felt252 {
            let tx_info = starknet::get_tx_info().unbox();
            let signature = tx_info.signature;
            assert(signature.len() == 2_u32, 'INVALID_SIGNATURE_LENGTH');
            assert(
                check_ecdsa_signature(
                    message_hash: tx_info.transaction_hash,
                    public_key: self.public_key.read(),
                    signature_r: *signature[0_u32],
                    signature_s: *signature[1_u32],
                ),
                'INVALID_SIGNATURE',
            );

            starknet::VALIDATED
        }
    }

    impl AccountContractImpl of starknet::account::AccountContract<ContractState> {
        fn __validate_declare__(self: @ContractState, class_hash: felt252) -> felt252 {
            self.validate_transaction()
        }

        fn __validate__(ref self: ContractState, calls: Array<Call>) -> felt252 {
            self.validate_transaction()
        }

        fn __execute__(ref self: ContractState, mut calls: Array<Call>) -> Array<Span<felt252>> {
            // Validate caller.
            assert(starknet::get_caller_address().is_zero(), 'INVALID_CALLER');

            // Check the tx version here, since version 0 transaction skip the __validate__ function.
            let tx_info = starknet::get_tx_info().unbox();
            assert(tx_info.version != 0, 'INVALID_TX_VERSION');

            let mut result = ArrayTrait::new();
            loop {
                match calls.pop_front() {
                    Option::Some(call) => {
                        let mut res = syscalls::call_contract_syscall(
                            address: call.to,
                            entry_point_selector: call.selector,
                            calldata: call.calldata
                        ).unwrap_syscall();
                        
                        result.append(res);
                    },
                    Option::None => {
                        break; // Can't break result; because of 'variable was previously moved'
                    },
                };
            };
            result
        }
    }
}