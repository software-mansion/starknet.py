import pytest

from starknet_py.compile.compiler import Compiler
from starknet_py.contract import Contract
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


async def declare_contract(account: BaseAccount):
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
    compiled_contract = Compiler(contract_source=contract).compile_contract()

    declare_result = await Contract.declare(
        account=account,
        compiled_contract=compiled_contract,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()


@pytest.mark.asyncio
async def test_pending_block(account):
    await declare_contract(account)

    blk = await account.client.get_block(block_number="pending")
    assert blk.block_hash


@pytest.mark.asyncio
async def test_latest_block(account):
    await declare_contract(account)

    blk = await account.client.get_block(block_number="latest")
    assert blk.block_hash
