from __future__ import annotations

import dataclasses
import warnings
from dataclasses import dataclass
from typing import Optional, TypeVar

from starknet_py.net.client import Client
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
@dataclass(frozen=True)
class SentTransaction:
    """
    Dataclass exposing the interface of transaction related to a performed action.
    """

    hash: int
    """Hash of the transaction."""

    _client: Client
    status: Optional[str] = None
    """Status of the transaction."""

    block_number: Optional[int] = None
    """Number of the block in which transaction was included."""

    async def wait_for_acceptance(
        self: TypeSentTransaction,
        wait_for_accept: Optional[bool] = None,
        check_interval: float = 2,
        retries: int = 500,
    ) -> TypeSentTransaction:
        """
        Waits for transaction to be accepted on chain till ``ACCEPTED`` status.
        Returns a new SentTransaction instance, **does not mutate original instance**.
        """
        if wait_for_accept is not None:
            warnings.warn(
                "Parameter `wait_for_accept` has been deprecated - since Starknet 0.12.0, transactions in a PENDING"
                " block have status ACCEPTED_ON_L2."
            )

        tx_receipt = await self._client.wait_for_tx(
            self.hash,
            check_interval=check_interval,
            retries=retries,
        )
        return dataclasses.replace(
            self,
            status=tx_receipt.finality_status,
            block_number=tx_receipt.block_number,
        )


TypeSentTransaction = TypeVar("TypeSentTransaction", bound="SentTransaction")
