import pytest

from starknet_py.tests.e2e.utils import deploy


@pytest.mark.asyncio
async def test_pending_block(new_account):
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
    await deploy(
        account=new_account,
        compilation_source=contract,
        constructor_args=constructor_args,
    )
    blk = await new_account.client.get_block(block_number="pending")
    assert blk.block_hash


@pytest.mark.asyncio
async def test_latest_block(new_account):
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
    await deploy(
        account=new_account,
        compilation_source=contract,
        constructor_args=constructor_args,
    )
    blk = await new_account.client.get_block(block_number="latest")
    assert blk.block_hash
