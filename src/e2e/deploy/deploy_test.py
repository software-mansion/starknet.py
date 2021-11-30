import aiounittest

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.gateway.transaction import Deploy
from starkware.starkware_utils.error_handling import StarkErrorCode

from src.e2e.utils import DevnetClient, file_from_directory

# Mock contract for deployment
import os

directory = os.path.dirname(__file__)


class DeployCase(aiounittest.AsyncTestCase):
    async def test_deploy_tx(self):
        client = DevnetClient()
        file_path = file_from_directory(directory, "example-compiled.json")
        contract_def = open(file_path, "r").read()

        result = await client.deploy_contract(contract_def)
        self.assertEquals(result["code"], StarkErrorCode.TRANSACTION_RECEIVED.name)
