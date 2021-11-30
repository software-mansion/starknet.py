import aiounittest

from starkware.starkware_utils.error_handling import StarkErrorCode

from src.contract import Contract
from src.e2e.utils import DevnetClient, file_from_directory

import os

directory = os.path.dirname(__file__)


class InteractionCase(aiounittest.AsyncTestCase):
    async def test_invoke_and_call(self):
        client = DevnetClient()

        # Deploy simple k-v store
        map_contract_file = file_from_directory(directory, "map-compiled.json")
        contract_def = open(map_contract_file, "r").read()
        result = await client.deploy_contract(contract_def)

        self.assertEquals(result["code"], StarkErrorCode.TRANSACTION_RECEIVED.name)
        contract_address = result["address"]

        await client.wait_for_tx(
            tx_hash=result["transaction_hash"],
        )

        contract = await Contract.from_address(address=contract_address, client=client)
        key, value = 123, 4320
        await contract.functions.put.invoke(key, value)

        result = await contract.functions.get.call(key)

        self.assertEquals(int(result[0], 16), value)
