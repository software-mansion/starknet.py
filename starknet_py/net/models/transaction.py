import dataclasses
import warnings
from abc import abstractmethod
from typing import Any, ClassVar, Dict, List, Sequence, Union

# noinspection PyPep8Naming
import marshmallow
import marshmallow_dataclass
from marshmallow import fields
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_declare_transaction_hash,
)
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.definitions.transaction_type import TransactionType as TT

# noinspection PyPep8Naming
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.gateway.transaction import DeployAccount as DAC
from starkware.starknet.services.api.gateway.transaction import InvokeFunction as IF
from starkware.starknet.services.api.gateway.transaction_utils import (
    compress_program,
    compress_program_post_dump,
    decompress_program,
)

from starknet_py.cairo.selector import get_selector_from_name
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.crypto.transaction_hash import (
    TransactionHashPrefix,
    compute_transaction_hash,
)
from starknet_py.utils.docs import as_our_module

Invoke = InvokeFunction = as_our_module(IF)
# Transaction = as_our_module(T)
TransactionType = as_our_module(TT)
# Declare = as_our_module(DCL)
DeployAccount = as_our_module(DAC)


@dataclasses.dataclass(frozen=True)
class Transaction:
    version: int = dataclasses.field(metadata={"marshmallow_field": Felt()})

    @classmethod
    @abstractmethod
    def tx_type(cls) -> TransactionType:
        """
        Returns the corresponding TransactionType enum. Used in TransacactionSchema.
        Subclasses should define it as a class variable.
        """

    @abstractmethod
    def calculate_hash(self, general_config: StarknetGeneralConfig) -> int:
        """
        Calculates the transaction hash in the StarkNet network - a unique identifier of the
        transaction. See calculate_transaction_hash_common() docstring for more details.
        """


@dataclasses.dataclass(frozen=True)  # type: ignore[misc]
class AccountTransaction(Transaction):
    """
    Represents a transaction in the StarkNet network that is originated from an action of an
    account.
    """

    # The maximal fee to be paid in Wei for executing the transaction.
    max_fee: int = dataclasses.field(metadata={"marshmallow_field": Felt()})
    # The signature of the transaction.
    # The exact way this field is handled is defined by the called contract's function,
    # similar to calldata.
    signature: List[int] = dataclasses.field(metadata={"marshmallow_field": fields.List(fields.String())})
    # The nonce of the transaction.
    # A sequential number attached to the account contract, that prevents transaction replay
    # and guarantees the order of execution and uniqueness of the transaction hash.


@dataclasses.dataclass(frozen=True)
class Declare(AccountTransaction):
    """
    Represents a transaction in the StarkNet network that is a declaration of a StarkNet contract
    class.
    """

    contract_class: ContractClass
    # The address of the account contract sending the declaration transaction.
    sender_address: int = dataclasses.field(metadata={"marshmallow_field": Felt()})
    # Repeat `nonce` to narrow its type to non-optional int.
    nonce: int = dataclasses.field(metadata={"marshmallow_field": Felt()})

    # Class variables.
    tx_type: ClassVar[TransactionType] = TransactionType.DECLARE

    @staticmethod
    def compress_program(program_json: dict):
        return compress_program(program_json=program_json)

    @marshmallow.decorators.post_dump
    def compress_program_post_dump(
        self, data: Dict[str, Any], many: bool, **kwargs
    ) -> Dict[str, Any]:
        data["type"] = "DECLARE"
        return compress_program_post_dump(data=data, many=many)

    @marshmallow.decorators.pre_load
    def decompress_program(
        self, data: Dict[str, Any], many: bool, **kwargs
    ) -> Dict[str, Any]:
        return decompress_program(data=data, many=many)

    def calculate_hash(self, general_config: StarknetGeneralConfig) -> int:
        """
        Calculates the transaction hash in the StarkNet network.
        """
        return calculate_declare_transaction_hash(
            contract_class=self.contract_class,
            chain_id=general_config.chain_id.value,
            sender_address=self.sender_address,
            max_fee=self.max_fee,
            version=self.version,
            nonce=self.nonce,
        )


DeclareSchema = marshmallow_dataclass.class_schema(Declare)


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
