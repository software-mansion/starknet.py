"""
Dataclasses representing Transactions for library use, most often
when sending a transaction to Starknet.
They should be compliant with the latest Starknet version.
"""

import base64
import dataclasses
import gzip
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, TypeVar

from marshmallow import fields

from starknet_py.hash.address import compute_address
from starknet_py.hash.transaction import (
    CommonTransactionV3Fields,
    TransactionHashPrefix,
    compute_declare_v3_transaction_hash,
    compute_deploy_account_v3_transaction_hash,
    compute_invoke_v3_transaction_hash,
)
from starknet_py.net.client_models import (
    DAMode,
    ResourceBoundsMapping,
    SierraContractClass,
    TransactionType,
)
from starknet_py.net.schemas.common import Felt

# TODO (#1219):
#  consider unifying these classes with client_models
#  remove marshmallow logic if not needed


@dataclass(frozen=True)
class Transaction(ABC):
    """
    Starknet transaction base class.
    """

    version: int = field(metadata={"marshmallow_field": Felt()})

    @property
    @abstractmethod
    def type(self) -> TransactionType:
        """
        Returns the corresponding TransactionType enum.
        """

    @abstractmethod
    def calculate_hash(self, chain_id: int) -> int:
        """
        Calculates the transaction hash in the Starknet network - a unique identifier of the
        transaction. See :py:meth:`~starknet_py.hash.transaction.compute_transaction_hash` docstring for more details.
        """


@dataclass(frozen=True)
class AccountTransaction(Transaction, ABC):
    """
    Represents a transaction in the Starknet network that is originated from an action of an
    account.
    """

    signature: List[int] = field(
        metadata={"marshmallow_field": fields.List(fields.String())}
    )
    nonce: int = field(metadata={"marshmallow_field": Felt()})


# Used instead of Union[Invoke, Declare, DeployAccount]
TypeAccountTransaction = TypeVar("TypeAccountTransaction", bound=AccountTransaction)


@dataclass(frozen=True)
class _DeprecatedAccountTransaction(AccountTransaction, ABC):
    max_fee: int = field(metadata={"marshmallow_field": Felt()})


@dataclass(frozen=True)
class _AccountTransactionV3(AccountTransaction, ABC):
    resource_bounds: ResourceBoundsMapping
    tip: int = field(init=False, default=0)
    nonce_data_availability_mode: DAMode = field(init=False, default=DAMode.L1)
    fee_data_availability_mode: DAMode = field(init=False, default=DAMode.L1)
    paymaster_data: List[int] = field(init=False, default_factory=list)

    def get_common_fields(
        self,
        tx_prefix: TransactionHashPrefix,
        address: int,
        chain_id: int,
    ) -> CommonTransactionV3Fields:
        common_fields = [f.name for f in dataclasses.fields(_AccountTransactionV3)]

        # this is a helper function in a process to compute transaction hash
        # therefore signature is not included at this point
        common_fields.remove("signature")

        common_fields_with_values = {
            field_name: getattr(self, field_name) for field_name in common_fields
        }

        return CommonTransactionV3Fields(
            tx_prefix=tx_prefix,
            address=address,
            chain_id=chain_id,
            **common_fields_with_values,
        )


@dataclass(frozen=True)
class DeclareV3(_AccountTransactionV3):
    """
    Represents a transaction in the Starknet network that is a version 3 declaration of a Starknet contract
    class. Supports only sierra compiled contracts.
    """

    sender_address: int
    compiled_class_hash: int
    contract_class: SierraContractClass
    account_deployment_data: List[int] = field(default_factory=list)

    @property
    def type(self) -> TransactionType:
        return TransactionType.DECLARE

    def calculate_hash(self, chain_id: int) -> int:
        return compute_declare_v3_transaction_hash(
            account_deployment_data=self.account_deployment_data,
            contract_class=self.contract_class,
            compiled_class_hash=self.compiled_class_hash,
            common_fields=self.get_common_fields(
                tx_prefix=TransactionHashPrefix.DECLARE,
                address=self.sender_address,
                chain_id=chain_id,
            ),
        )


# pylint: enable=line-too-long


@dataclass(frozen=True)
class DeployAccountV3(_AccountTransactionV3):
    """
    Represents a transaction in the Starknet network that is a version 3 deployment of a Starknet account
    contract.
    """

    class_hash: int
    contract_address_salt: int
    constructor_calldata: List[int]

    @property
    def type(self) -> TransactionType:
        return TransactionType.DEPLOY_ACCOUNT

    def calculate_hash(self, chain_id: int) -> int:
        contract_address = compute_address(
            salt=self.contract_address_salt,
            class_hash=self.class_hash,
            constructor_calldata=self.constructor_calldata,
            deployer_address=0,
        )
        return compute_deploy_account_v3_transaction_hash(
            class_hash=self.class_hash,
            constructor_calldata=self.constructor_calldata,
            contract_address_salt=self.contract_address_salt,
            common_fields=self.get_common_fields(
                tx_prefix=TransactionHashPrefix.DEPLOY_ACCOUNT,
                address=contract_address,
                chain_id=chain_id,
            ),
        )


@dataclass(frozen=True)
class InvokeV3(_AccountTransactionV3):
    """
    Represents a transaction in the Starknet network that is a version 3 invocation of a Cairo contract
    function.
    """

    calldata: List[int]
    sender_address: int
    account_deployment_data: List[int] = field(default_factory=list)

    @property
    def type(self) -> TransactionType:
        return TransactionType.INVOKE

    def calculate_hash(self, chain_id: int) -> int:
        return compute_invoke_v3_transaction_hash(
            account_deployment_data=self.account_deployment_data,
            calldata=self.calldata,
            common_fields=self.get_common_fields(
                tx_prefix=TransactionHashPrefix.INVOKE,
                address=self.sender_address,
                chain_id=chain_id,
            ),
        )


def compress_program(data: dict, program_name: str = "program") -> dict:
    program = data["contract_class"][program_name]
    compressed_program = json.dumps(program)
    compressed_program = gzip.compress(data=compressed_program.encode("ascii"))
    compressed_program = base64.b64encode(compressed_program)
    data["contract_class"][program_name] = compressed_program.decode("ascii")
    return data


def decompress_program(data: dict, program_name: str = "program") -> dict:
    compressed_program: str = data["contract_class"][program_name]
    program = base64.b64decode(compressed_program.encode("ascii"))
    program = gzip.decompress(data=program)
    program = json.loads(program.decode("ascii"))
    data["contract_class"][program_name] = program
    return data
