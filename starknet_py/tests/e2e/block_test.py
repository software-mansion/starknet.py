import pytest

from starknet_py.contract import Contract


@pytest.mark.asyncio
async def test_pending_block(gateway_account_client):
    contract = """
        %lang starknet
        %builtins pedersen range_check
        
        from starkware.cairo.common.cairo_builtins import HashBuiltin
        
        @storage_var
        func public_key() -> (res: felt) {
        }
        
        @constructor
        func constructor{syscall_ptr: felt*, range_check_ptr: felt, pedersen_ptr: HashBuiltin*}(
            pkey: felt
        ) {
            public_key.write(pkey);
            return ();
        }
    """

    constructor_args = [123]
    await Contract.deploy(
        gateway_account_client,
        compilation_source=contract,
        constructor_args=constructor_args,
    )
    blk = await gateway_account_client.get_block(block_number="pending")
    assert blk.block_hash


@pytest.mark.asyncio
async def test_latest_block(gateway_account_client):
    contract = """
        %lang starknet
        %builtins pedersen range_check
        
        from starkware.cairo.common.cairo_builtins import HashBuiltin
        
        @storage_var
        func public_key() -> (res: felt) {
        }
        
        @constructor
        func constructor{syscall_ptr: felt*, range_check_ptr: felt, pedersen_ptr: HashBuiltin*}(
            pkey: felt
        ) {
            public_key.write(pkey);
            return ();
        }
    """

    constructor_args = [123]
    await Contract.deploy(
        gateway_account_client,
        compilation_source=contract,
        constructor_args=constructor_args,
    )
    blk = await gateway_account_client.get_block(block_number="latest")
    assert blk.block_hash
