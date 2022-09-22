from typing import Optional, List

from starknet_py.net.client_models import Hash
from starknet_py.net.deployer.contract_deployment import ContractDeployment
from starknet_py.net.models import AddressRepresentation


class Deployer:
    """
    Deployer used to deploy contracts through Universal Deployer Contract (UDC)
    """

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
        """
        Creates a ContractDeployment instance which is used to prepare and send deploy invoke transactions

        :param class_hash: The class_hash of the contract to be deployed
        :param abi: ABI of the contract to be deployed
        :returns: ContractDeployment
        """
        return ContractDeployment(deployer=self, class_hash=class_hash, abi=abi)
