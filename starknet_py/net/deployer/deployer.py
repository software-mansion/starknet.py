from typing import Optional, List

from starknet_py.net.client_models import Hash
from starknet_py.net.deployer.contract_deployment import ContractDeployment
from starknet_py.net.models import AddressRepresentation


class Deployer:
    def __init__(
        self,
        account: "AccountClient",
        address: AddressRepresentation,
        salt: Optional[int] = None,
        unique: bool = True,
    ):
        self.account = account
        self.address = address
        self.salt = salt
        self.unique = unique

    def for_contract(self, class_hash: Hash, abi: Optional[List] = None):
        return ContractDeployment(deployer=self, class_hash=class_hash, abi=abi)
