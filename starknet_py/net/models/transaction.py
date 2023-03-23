"""
Dataclasses representing Transactions for library use, most often
when sending a transaction to Starknet.
They should be compliant with the latest Starknet version.
"""

import base64
import gzip
import json
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, TypeVar, Union

import marshmallow
import marshmallow_dataclass
from marshmallow import fields

from starknet_py.constants import DEFAULT_ENTRY_POINT_SELECTOR
from starknet_py.hash.address import compute_address
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.transaction import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_declare_v2_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_transaction_hash,
)
from starknet_py.net.client_models import (
    ContractClass,
    SierraContractClass,
    TransactionType,
)
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.schemas.common import Felt, TransactionTypeField
from starknet_py.net.schemas.gateway import (
    ContractClassSchema,
    SierraContractClassSchema,
)


@dataclass(frozen=True)
class Transaction(ABC):
    """
    StarkNet transaction base class.
    """

    version: int = field(metadata={"marshmallow_field": Felt()})

    @property
    @abstractmethod
    def type(self) -> TransactionType:
        """
        Returns the corresponding TransactionType enum.
        """

    @abstractmethod
    def calculate_hash(self, chain_id: StarknetChainId) -> int:
        """
        Calculates the transaction hash in the StarkNet network - a unique identifier of the
        transaction. See :ref:`compute_transaction_hash` docstring for more details.
        """


@dataclass(frozen=True)
class AccountTransaction(Transaction, ABC):
    """
    Represents a transaction in the StarkNet network that is originated from an action of an
    account.
    """

    max_fee: int = field(metadata={"marshmallow_field": Felt()})
    signature: List[int] = field(
        metadata={"marshmallow_field": fields.List(fields.String())}
    )
    nonce: int = field(metadata={"marshmallow_field": Felt()})


# Used instead of Union[Invoke, Declare, DeployAccount]
TypeAccountTransaction = TypeVar("TypeAccountTransaction", bound=AccountTransaction)


@dataclass(frozen=True)
class DeclareV2(AccountTransaction):
    """
    Represents a transaction in the Starknet network that is a version 2 declaration of a Starknet contract
    class. Supports only sierra compiled contracts.
    """

    contract_class: SierraContractClass = field(
        metadata={"marshmallow_field": fields.Nested(SierraContractClassSchema())}
    )
    compiled_class_hash: int = field(metadata={"marshmallow_field": Felt()})
    sender_address: int = field(metadata={"marshmallow_field": Felt()})
    type: TransactionType = field(
        metadata={"marshmallow_field": TransactionTypeField()},
        default=TransactionType.DECLARE,
    )

    @marshmallow.post_dump
    def post_dump(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        # pylint: disable=unused-argument, no-self-use
        return compress_program(data, program_name="sierra_program")

    @marshmallow.pre_load
    def pre_load(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        # pylint: disable=unused-argument, no-self-use
        return decompress_program(data, program_name="sierra_program")

    def calculate_hash(self, chain_id: StarknetChainId) -> int:
        return compute_declare_v2_transaction_hash(
            contract_class=self.contract_class,
            compiled_class_hash=self.compiled_class_hash,
            chain_id=chain_id.value,
            sender_address=self.sender_address,
            max_fee=self.max_fee,
            version=self.version,
            nonce=self.nonce,
        )


@dataclass(frozen=True)
class Declare(AccountTransaction):
    """
    Represents a transaction in the StarkNet network that is a declaration of a StarkNet contract
    class.
    """

    contract_class: ContractClass = field(
        metadata={"marshmallow_field": fields.Nested(ContractClassSchema())}
    )
    # The address of the account contract sending the declaration transaction.
    sender_address: int = field(metadata={"marshmallow_field": Felt()})
    type: TransactionType = field(
        metadata={"marshmallow_field": TransactionTypeField()},
        default=TransactionType.DECLARE,
    )

    @marshmallow.post_dump
    def post_dump(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        # Allowing **kwargs is needed here because marshmallow is passing additional parameters here
        # along with data, which we don't handle.
        # pylint: disable=unused-argument, no-self-use
        return compress_program(data)

    @marshmallow.pre_load
    def pre_load(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        # pylint: disable=unused-argument, no-self-use
        return decompress_program(data)

    def calculate_hash(self, chain_id: StarknetChainId) -> int:
        """
        Calculates the transaction hash in the StarkNet network.
        """
        return compute_declare_transaction_hash(
            contract_class=self.contract_class,
            chain_id=chain_id.value,
            sender_address=self.sender_address,
            max_fee=self.max_fee,
            version=self.version,
            nonce=self.nonce,
        )


@dataclass(frozen=True)
class DeployAccount(AccountTransaction):
    """
    Represents a transaction in the StarkNet network that is a deployment of a StarkNet account
    contract.
    """

    class_hash: int = field(metadata={"marshmallow_field": Felt()})
    contract_address_salt: int = field(metadata={"marshmallow_field": Felt()})
    constructor_calldata: List[int] = field(
        metadata={"marshmallow_field": fields.List(fields.String())}
    )

    type: TransactionType = field(
        metadata={"marshmallow_field": TransactionTypeField()},
        default=TransactionType.DEPLOY_ACCOUNT,
    )

    def calculate_hash(self, chain_id: StarknetChainId) -> int:
        """
        Calculates the transaction hash in the StarkNet network.
        """
        contract_address = compute_address(
            salt=self.contract_address_salt,
            class_hash=self.class_hash,
            constructor_calldata=self.constructor_calldata,
            deployer_address=0,
        )
        return compute_deploy_account_transaction_hash(
            version=self.version,
            contract_address=contract_address,
            class_hash=self.class_hash,
            constructor_calldata=self.constructor_calldata,
            max_fee=self.max_fee,
            nonce=self.nonce,
            salt=self.contract_address_salt,
            chain_id=chain_id.value,
        )


@dataclass(frozen=True)
class Invoke(AccountTransaction):
    """
    Represents a transaction in the StarkNet network that is an invocation of a Cairo contract
    function.
    """

    sender_address: int = field(metadata={"marshmallow_field": Felt()})
    calldata: List[int] = field(
        metadata={"marshmallow_field": fields.List(fields.String())}
    )

    type: TransactionType = field(
        metadata={"marshmallow_field": TransactionTypeField()},
        default=TransactionType.INVOKE,
    )

    def calculate_hash(self, chain_id: StarknetChainId) -> int:
        """
        Calculates the transaction hash in the StarkNet network.
        """
        return compute_transaction_hash(
            tx_hash_prefix=TransactionHashPrefix.INVOKE,
            version=self.version,
            contract_address=self.sender_address,
            entry_point_selector=DEFAULT_ENTRY_POINT_SELECTOR,
            calldata=self.calldata,
            max_fee=self.max_fee,
            chain_id=chain_id.value,
            additional_data=[self.nonce],
        )


InvokeSchema = marshmallow_dataclass.class_schema(Invoke)
DeclareSchema = marshmallow_dataclass.class_schema(Declare)
DeclareV2Schema = marshmallow_dataclass.class_schema(DeclareV2)
DeployAccountSchema = marshmallow_dataclass.class_schema(DeployAccount)


def compute_invoke_hash(
    sender_address: int,
    entry_point_selector: Union[int, str],
    calldata: Sequence[int],
    chain_id: StarknetChainId,
    max_fee: int,
    version: int,
) -> int:
    # pylint: disable=too-many-arguments
    """
    Computes invocation hash.

    :param sender_address: int
    :param entry_point_selector: Union[int, str]
    :param calldata: Sequence[int]
    :param chain_id: StarknetChainId
    :param max_fee: Max fee
    :param version: Contract version
    :return: calculated hash
    """
    warnings.warn(
        "Function compute_invoke_hash is deprecated."
        "To compute hash of an invoke transaction use compute_transaction_hash.",
        category=DeprecationWarning,
    )

    if isinstance(entry_point_selector, str):
        entry_point_selector = get_selector_from_name(entry_point_selector)

    return compute_transaction_hash(
        tx_hash_prefix=TransactionHashPrefix.INVOKE,
        contract_address=sender_address,
        entry_point_selector=entry_point_selector,
        calldata=calldata,
        chain_id=chain_id.value,
        additional_data=[],
        max_fee=max_fee,
        version=version,
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
