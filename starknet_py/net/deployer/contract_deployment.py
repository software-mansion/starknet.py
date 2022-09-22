from typing import Optional, List, Union

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net.client_models import Hash, InvokeFunction, Call
from starknet_py.utils.contructor_args_translator import translate_constructor_args
from starknet_py.utils.data_transformer.universal_deployer_serializer import (
    universal_deployer_serializer,
    deploy_contract_abi,
    deploy_contract_event_abi,
)


class ContractDeployment:
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

    async def send_transaction(self, deploy_invoke_transaction: InvokeFunction) -> int:
        resp = await self.deployer.account.send_transaction(
            transaction=deploy_invoke_transaction
        )
        await self.deployer.account.wait_for_tx(resp.transaction_hash)

        receipt = await self.deployer.account.get_transaction_receipt(
            tx_hash=resp.transaction_hash
        )
        event = universal_deployer_serializer.to_python(
            value_types=deploy_contract_event_abi["data"], values=receipt.events[0].data
        )

        return event.contractAddress
