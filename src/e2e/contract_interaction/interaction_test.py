import pytest
import os
from starkware.starkware_utils.error_handling import StarkErrorCode

from src.contract import Contract
from src.e2e.utils import DevnetClient
from src.utils.compiler.starknet_compile import CairoSourceFile
from src.utils.files import file_from_directory

directory = os.path.dirname(__file__)


@pytest.mark.asyncio
@pytest.mark.parametrize("key, value", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_and_call(key, value):
    client = DevnetClient()

    map_file = file_from_directory(directory, "map.cairo")
    map_source_code = open(map_file).read()
    # Deploy simple k-v store
    result = await client.compile_and_deploy_contract(
        [CairoSourceFile(content=map_source_code, name=map_file)]
    )

    assert result["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name
    contract_address = result["address"]

    await client.wait_for_tx(
        tx_hash=result["transaction_hash"],
    )

    contract = await Contract.from_address(address=contract_address, client=client)
    await contract.functions.put.invoke(key, value)

    response = await contract.functions.get.call(key)

    assert response["res"] == value
