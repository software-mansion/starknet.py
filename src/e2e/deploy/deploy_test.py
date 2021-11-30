import aiounittest

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.gateway.transaction import Deploy
from starkware.starkware_utils.error_handling import StarkErrorCode

from src.e2e.utils import DevnetClient

# Mock contract for deployment
import os

dirname = os.path.dirname(__file__)
test_contract_file = os.path.join(dirname, "example-compiled.json")


class DeployCase(aiounittest.AsyncTestCase):
    async def test_deploy_tx(self):
        client = DevnetClient()
        compiled_def = open(test_contract_file, "r").read()
        contract_def = ContractDefinition.loads(compiled_def)

        result = await client.add_transaction(
            tx=Deploy(
                contract_address_salt=ContractAddressSalt.get_random_value(),
                contract_definition=contract_def,
                constructor_calldata=[],
            )
        )
        self.assertEquals(result["code"], StarkErrorCode.TRANSACTION_RECEIVED.name)
