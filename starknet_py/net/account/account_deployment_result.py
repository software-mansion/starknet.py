from dataclasses import dataclass

from starknet_py.contract import SentTransaction
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
@dataclass(frozen=True)
class AccountDeploymentResult(SentTransaction):
    account: "Account" = None  # pyright: ignore

    def __post_init__(self):
        if self.account is None:
            raise ValueError("Account cannot be None in AccountDeploymentResult")
