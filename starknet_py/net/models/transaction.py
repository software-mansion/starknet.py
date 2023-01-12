import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, TypeVar, Union

import marshmallow
import marshmallow_dataclass
from marshmallow import fields
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.gateway.transaction_utils import (
    compress_program_post_dump,
    decompress_program,
)

from starknet_py.cairo.selector import get_selector_from_name
from starknet_py.net.client_models import TransactionType
from starknet_py.net.models import compute_address
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.schemas.common import Felt, NoneFelt
from starknet_py.utils.crypto.transaction_hash import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_transaction_hash,
)


# pylint: disable=no-self-use, unused-argument
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
class AccountTransaction(Transaction):
    """
    Represents a transaction in the StarkNet network that is originated from an action of an
    account.
    """

    max_fee: int = field(metadata={"marshmallow_field": Felt()})
    signature: List[int] = field(
        metadata={"marshmallow_field": fields.List(fields.String())}
    )
    nonce: int = field(metadata={"marshmallow_field": Felt()})


# Used in the Account instead of Union[Invoke, Declare, DeployAccount]
TypeAccountTransaction = TypeVar("TypeAccountTransaction", bound=AccountTransaction)


@dataclass(frozen=True)
class Declare(AccountTransaction):
    """
    Represents a transaction in the StarkNet network that is a declaration of a StarkNet contract
    class.
    """

    contract_class: ContractClass
    # The address of the account contract sending the declaration transaction.
    sender_address: int = field(metadata={"marshmallow_field": Felt()})
    type: TransactionType = TransactionType.DECLARE

    @marshmallow.post_dump
    def compress_program_post_dump(
        self, data: Dict[str, Any], many: bool, **kwargs
    ) -> Dict[str, Any]:
        return compress_program_post_dump(data=data, many=many)

    @marshmallow.pre_load
    def decompress_program(
        self, data: Dict[str, Any], many: bool, **kwargs
    ) -> Dict[str, Any]:
        return decompress_program(data=data, many=many)

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
    version: int = field(metadata={"marshmallow_field": Felt()})

    type: TransactionType = TransactionType.DEPLOY_ACCOUNT

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

    contract_address: int = field(metadata={"marshmallow_field": Felt()})
    calldata: List[int] = field(
        metadata={"marshmallow_field": fields.List(fields.String())}
    )
    nonce: Optional[int] = field(metadata={"marshmallow_field": NoneFelt()})
    # A field element that encodes the signature of the invoked function.
    # The entry_point_selector is deprecated for version 1 and above (transactions
    # should go through the '__execute__' entry point).
    entry_point_selector: Optional[int] = field(
        default=None, metadata={"marshmallow_field": NoneFelt()}
    )

    type: TransactionType = TransactionType.INVOKE

    @marshmallow.post_dump
    def _remove_entry_point_selector(
        self, data: Dict[str, Any], many: bool, **kwargs
    ) -> Dict[str, Any]:
        data["type"] = "INVOKE_FUNCTION"

        version = int(data["version"], 16)
        if version == 0:
            return data

        assert (
            data["entry_point_selector"] is None
        ), f"entry_point_selector should be None in version {version}."
        del data["entry_point_selector"]

        return data

    def calculate_hash(self, chain_id: StarknetChainId) -> int:
        """
        Calculates the transaction hash in the StarkNet network.
        """
        if self.version == 0:
            assert (
                self.nonce is None
            ), f"nonce is not None ({self.nonce}) for version={self.version}."
            additional_data = []
            assert (
                self.entry_point_selector is not None
            ), f"entry_point_selector is None for version={self.version}."
            entry_point_selector_field = self.entry_point_selector
        else:
            assert self.nonce is not None, f"nonce is None for version={self.version}."
            additional_data = [self.nonce]
            assert (
                self.entry_point_selector is None
            ), f"entry_point_selector is deprecated in version={self.version}."
            entry_point_selector_field = 0

        return compute_transaction_hash(
            tx_hash_prefix=TransactionHashPrefix.INVOKE,
            version=self.version,
            contract_address=self.contract_address,
            entry_point_selector=entry_point_selector_field,
            calldata=self.calldata,
            max_fee=self.max_fee,
            chain_id=chain_id.value,
            additional_data=additional_data,
        )


InvokeSchema = marshmallow_dataclass.class_schema(Invoke)
DeclareSchema = marshmallow_dataclass.class_schema(Declare)
DeployAccountSchema = marshmallow_dataclass.class_schema(DeployAccount)


def compute_invoke_hash(
    contract_address: int,
    entry_point_selector: Union[int, str],
    calldata: Sequence[int],
    chain_id: StarknetChainId,
    max_fee: int,
    version: int,
) -> int:
    # pylint: disable=too-many-arguments
    """
    Computes invocation hash.

    :param contract_address: int
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
        contract_address=contract_address,
        entry_point_selector=entry_point_selector,
        calldata=calldata,
        chain_id=chain_id.value,
        additional_data=[],
        max_fee=max_fee,
        version=version,
    )
