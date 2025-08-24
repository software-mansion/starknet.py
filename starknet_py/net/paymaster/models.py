"""
Models for the Paymaster API.

This module contains data models used by the PaymasterClient for interacting with
the Applicative Paymaster API.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from starknet_py.net.client_models import Call, OutsideExecutionTimeBounds
from starknet_py.utils.typed_data import TypedData


@dataclass
class TokenData:
    """
    Object containing data about the token: contract address, number of decimals and current price in STRK.
    """

    token_address: str
    """Token contract address"""

    decimals: int
    """The number of decimals of the token"""

    price_in_strk: int
    """Price in STRK (in FRI units)"""


class TrackingStatus(str, Enum):
    """
    Status of a transaction tracking ID.
    """

    ACTIVE = "active"
    ACCEPTED = "accepted"
    DROPPED = "dropped"


@dataclass
class TrackingIdResponse:
    """
    Response for tracking ID to latest int request.
    """

    transaction_hash: int
    status: TrackingStatus


@dataclass
class FeeMode:
    """
    Base class for fee modes.
    """

    mode: str


@dataclass
class SponsoredFeeMode(FeeMode):
    """
    Specify that the transaction should be sponsored.
    """

    mode: str = "sponsored"


@dataclass
class DefaultFeeMode(FeeMode):
    """
    Default fee mode where the transaction is paid by the user in the given gas token.
    """

    gas_token: int
    """The token to use for paying gas fees"""

    mode: str = "default"


@dataclass
class PriorityFeeMode(FeeMode):
    """
    Fee mode where the transaction is paid by the user in the given gas token and the user can specify a tip.
    """

    gas_token: int
    """The token to use for paying gas fees"""

    tip_in_strk: int
    """Additional tip in STRK"""

    mode: str = "priority"


@dataclass
class UserParameters:
    """
    Execution parameters to be used when executing the transaction through the paymaster.
    """

    fee_mode: FeeMode
    version: str = "0x1"
    time_bounds: Optional[OutsideExecutionTimeBounds] = None


@dataclass
class AccountDeploymentData:
    """
    Data required to deploy an account at an address.
    """

    address: int
    class_hash: int
    salt: int
    calldata: List[int]
    version: int = 1
    sigdata: Optional[List[int]] = None


@dataclass
class UserInvoke:
    """
    Invoke data to a transaction on behalf of the user.
    """

    user_address: int
    """The address of the user account"""

    calls: List[Call]
    """The sequence of calls that the user wishes to perform"""


@dataclass
class UserTransaction:
    """
    Base class for user transactions.
    """

    type: str


@dataclass
class DeployTransaction(UserTransaction):
    """
    Deployment transaction.
    """

    deployment: AccountDeploymentData
    """Deployment data necessary to deploy the account"""

    type: str = "deploy"


@dataclass
class InvokeTransaction(UserTransaction):
    """
    Invoke transaction.
    """

    invoke: UserInvoke
    """Invoke data to a transaction on behalf of the user"""

    type: str = "invoke"


@dataclass
class DeployAndInvokeTransaction(UserTransaction):
    """
    Deploy and invoke transaction.
    """

    deployment: AccountDeploymentData
    """Deployment data necessary to deploy the account"""

    invoke: UserInvoke
    """Invoke data to a transaction on behalf of the user"""

    type: str = "deploy_and_invoke"


@dataclass
class FeeEstimate:
    """
    Fee estimation for a transaction.
    """

    gas_token_price_in_strk: int
    estimated_fee_in_strk: int
    estimated_fee_in_gas_token: int
    suggested_max_fee_in_strk: int
    suggested_max_fee_in_gas_token: int


@dataclass
class ExecutableUserInvoke:
    """
    Invoke data signed by the user to be executed by the paymaster service.
    """

    user_address: int
    """The address of the user account"""

    typed_data: TypedData
    """Typed data returned by the endpoint paymaster_buildTransaction"""

    signature: List[int]
    """Signature of the associated Typed Data"""


@dataclass
class ExecutableUserTransaction:
    """
    Base class for executable user transactions.
    """

    type: str


@dataclass
class ExecutableDeployTransaction(ExecutableUserTransaction):
    """
    Executable deployment transaction.
    """

    deployment: AccountDeploymentData
    """Deployment data necessary to deploy the account"""

    type: str = "deploy"


@dataclass
class ExecutableInvokeTransaction(ExecutableUserTransaction):
    """
    Executable invoke transaction.
    """

    invoke: ExecutableUserInvoke
    """Invoke data signed by the user to be executed by the paymaster service"""

    type: str = "invoke"


@dataclass
class ExecutableDeployAndInvokeTransaction(ExecutableUserTransaction):
    """
    Executable deploy and invoke transaction.
    """

    deployment: AccountDeploymentData
    """Deployment data necessary to deploy the account"""

    invoke: ExecutableUserInvoke
    """Invoke data signed by the user to be executed by the paymaster service"""

    type: str = "deploy_and_invoke"


@dataclass
class ExecuteTransactionResponse:
    """
    Response for execute transaction request.
    """

    tracking_id: int
    transaction_hash: int


class BuildTransactionResponseType(str, Enum):
    """
    Type of build transaction response.
    """

    DEPLOY = "deploy"
    INVOKE = "invoke"
    DEPLOY_AND_INVOKE = "deploy_and_invoke"


@dataclass
class BuildTransactionResponse:
    """
    Base class for build transaction responses.
    """

    type: BuildTransactionResponseType
    parameters: UserParameters
    fee: FeeEstimate


@dataclass
class DeployBuildTransactionResponse(BuildTransactionResponse):
    """
    Response for build transaction request for deployment.
    """

    deployment: AccountDeploymentData


@dataclass
class InvokeBuildTransactionResponse(BuildTransactionResponse):
    """
    Response for build transaction request for invoke.
    """

    typed_data: TypedData


@dataclass
class DeployAndInvokeBuildTransactionResponse(BuildTransactionResponse):
    """
    Response for build transaction request for deploy and invoke.
    """

    deployment: AccountDeploymentData
    typed_data: TypedData
