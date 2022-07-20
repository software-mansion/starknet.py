import os
import pytest

directory = os.path.dirname(__file__)


@pytest.mark.asyncio
async def test_deploying_new_contracts(gateway_client):
    # pylint: disable=import-outside-toplevel, disable=duplicate-code
    # add to docs: start
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.contract import Contract
    from pathlib import Path
    from starknet_py.net.networks import TESTNET

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
                pedersen_ptr : HashBuiltin*,
                range_check_ptr
            }(_public_key: felt):
            public_key.write(_public_key)
            return ()
        end
        """

    client = GatewayClient(TESTNET)
    # add to docs: end
    client = gateway_client
    # add to docs: start

    # Use list for positional arguments
    constructor_args = [123]

    # or use dict for keyword arguments
    constructor_args = {"_public_key": 123}

    # contract as a string
    deployment_result = await Contract.deploy(
        client, compilation_source=contract, constructor_args=constructor_args
    )

    # list with filepaths - useful for multiple files
    deployment_result = await Contract.deploy(
        client,
        compilation_source=[Path(directory, "contract.cairo")],
        constructor_args=constructor_args,
    )

    # or use already compiled program
    compiled = Path(directory, "contract_compiled.json").read_text("utf-8")
    deployment_result = await Contract.deploy(
        client, compiled_contract=compiled, constructor_args=constructor_args
    )

    # you can wait for transaction to be accepted
    await deployment_result.wait_for_acceptance()

    # but you can access the deployed contract object even if has not been accepted yet
    contract = deployment_result.deployed_contract
    # add to docs: end
