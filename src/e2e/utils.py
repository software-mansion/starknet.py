import os

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.gateway.transaction import Deploy

from src.net import Client


class DevnetClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__("http://localhost:5000", *args, **kwargs)

    async def deploy_contract(self, contract_def_json: str):
        contract_def = ContractDefinition.loads(contract_def_json)

        return await self.add_transaction(
            tx=Deploy(
                contract_address_salt=ContractAddressSalt.get_random_value(),
                contract_definition=contract_def,
                constructor_calldata=[],
            )
        )


def file_from_directory(directory: str, filename: str) -> str:
    return os.path.join(directory, filename)
