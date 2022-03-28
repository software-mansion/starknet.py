import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.utils import DevnetClient


@pytest.mark.asyncio
async def test_pending_block():
    contract = """
    %lang starknet
    %builtins pedersen range_check

    from starkware.cairo.common.cairo_builtins import HashBuiltin

    @storage_var
    func public_key() -> (res: felt):
    end

    @constructor
    func constructor{
            syscall_ptr : felt*,
            range_check_ptr : felt,
            pedersen_ptr : HashBuiltin*
        }(pkey: felt):
        public_key.write(pkey)
        return ()
    end
    """

    client = await DevnetClient.make_devnet_client()
    constructor_args = [123]
    await Contract.deploy(
        client, compilation_source=contract, constructor_args=constructor_args
    )
    blk = await client.get_block(block_number="pending")
    assert blk.block_hash
