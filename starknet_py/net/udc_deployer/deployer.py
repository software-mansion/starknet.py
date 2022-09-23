from typing import Optional, List, Union

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net import AccountClient
from starknet_py.net.client_models import Hash, InvokeFunction, Call, Event
from starknet_py.net.models import AddressRepresentation
from starknet_py.net.models.deployer_addresses import deployer_address_from_network
from starknet_py.utils.contructor_args_translator import translate_constructor_args
from starknet_py.utils.data_transformer.universal_deployer_serializer import (
    universal_deployer_serializer,
    deploy_contract_abi,
    deploy_contract_event_abi,
)


class Deployer:
    """
    Deployer used to deploy contracts through Universal Deployer Contract (UDC)
    """

    def __init__(
        self,
        account: AccountClient,
        address: Optional[AddressRepresentation] = None,
        salt: Optional[int] = None,
        unique: bool = True,
    ):
        """
        :param account: AccountClient used to sign and send transactions
        :param address: Address of the UDC. Must be set when using a custom network
        :param salt: The salt for a contract to be deployed. Random value is selected if it is not provided
        :param unique: Boolean determining if the salt should be connected with the account's address. Default to True
        """
        address = address or deployer_address_from_network(
            net=account.net, deployer_address=address
        )

        self.account = account
        self.address = address
        self.salt = salt
        self.unique = unique

    def make_deployment(self, class_hash: Hash, abi: Optional[List] = None):
        """
        Creates a ContractDeployment instance which is used to prepare and send deploy invoke transactions

        :param class_hash: The class_hash of the contract to be deployed
        :param abi: ABI of the contract to be deployed
        :returns: ContractDeployment
        """

        return Deployer.ContractDeployment(
            deployer=self, class_hash=class_hash, abi=abi
        )

    async def get_deployed_contract_address(self, transaction_hash: Hash) -> int:
        """
        Returns deployed contract address

        :param transaction_hash: Hash of the already send and accepted deploy invoke transaction
        :returns: An address of the deployed contract
        """
        event = await self._get_deploy_event(transaction_hash=transaction_hash)

        if not event:
            raise ValueError(
                "ContractDeployed event was not found."
                "Make sure that transaction_hash is the hash of UDC deploy transaction"
            )

        event = universal_deployer_serializer.to_python(
            value_types=deploy_contract_event_abi["data"],
            values=event.data,
        )

        return event.contractAddress

    async def _get_deploy_event(self, transaction_hash: Hash) -> Optional[Event]:
        receipt = await self.account.get_transaction_receipt(tx_hash=transaction_hash)

        for event in receipt.events:
            if get_selector_from_name("ContractDeployed") == event.keys[0]:
                return event
        return None

    class ContractDeployment:
        """
        ContractDeployment used to prepare and send deploy invoke transactions
        """

        def __init__(
            self, deployer: "Deployer", class_hash: Hash, abi: Optional[List] = None
        ):
            self.deployer = deployer
            self.class_hash = class_hash
            self.abi: List = abi or []

        async def prepare_transaction(
            self,
            constructor_calldata: Optional[Union[List[any], dict]] = None,
            max_fee: Optional[int] = None,
            auto_estimate: bool = False,
        ) -> InvokeFunction:
            """
            Prepares deploy invoke transaction

            :param constructor_calldata: Constructor args of the contract to be deployed
            :param max_fee: Max amount of Wei to be paid when executing transaction
            :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
            :return: InvokeFunction
            """
            if not self.abi and constructor_calldata:
                raise ValueError("constructor_calldata was provided without an abi")

            constructor_calldata = translate_constructor_args(
                abi=self.abi or [], constructor_args=constructor_calldata
            )

            calldata, _ = universal_deployer_serializer.from_python(
                value_types=deploy_contract_abi["inputs"],
                class_hash=self.class_hash
                if isinstance(self.class_hash, int)
                else int(self.class_hash, 16),
                salt=self.deployer.salt or ContractAddressSalt.get_random_value(),
                unique=int(self.deployer.unique),
                constructor_calldata=constructor_calldata,
            )

            call = Call(
                to_addr=self.deployer.address,
                selector=get_selector_from_name("deployContract"),
                calldata=calldata,
            )

            transaction = await self.deployer.account.sign_invoke_transaction(
                calls=call, max_fee=max_fee, auto_estimate=auto_estimate
            )

            return transaction
