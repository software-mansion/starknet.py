import os.path
from pathlib import Path
import pytest

from starknet.contract import Contract
from starknet.net.account.account_client import AccountClient


directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_deploy_account_contract_and_sign_tx():
    acc_client = await AccountClient.create_account(net="http://localhost:5000/")

    map_contract = await Contract.deploy(
        client=acc_client, compilation_source=map_source_code
    )
    k, v = 13, 4324
    await map_contract.functions["put"].invoke(k, v)
    (resp,) = await map_contract.functions["get"].call(k)

    assert resp == v
