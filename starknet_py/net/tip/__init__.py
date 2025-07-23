import math
import statistics
from typing import Optional, Union

from starknet_py.net.client import Client
from starknet_py.net.client_models import Hash, Tag, TransactionV3


async def estimate_tip(
    client: Client,
    block_hash: Optional[Union[Hash, Tag]] = None,
    block_number: Optional[Union[int, Tag]] = None,
) -> int:
    """
    Estimates the transaction tip by taking the median of all V3 transaction tips in the specified block.
    If no block is provided, the `pre-confirmed` block is used.

    :param client: Client instance.
    :param block_hash: Block's hash or literals `"latest" or "pre_confirmed"`
    :param block_number: Block's number or literals `"latest" or "pre_confirmed"``
    """
    if block_hash is None and block_number is None:
        block_hash = "pre_confirmed"

    block_with_txs = await client.get_block_with_txs(block_hash, block_number)

    tips = [
        tx.tip for tx in block_with_txs.transactions if isinstance(tx, TransactionV3)
    ]

    if len(tips) == 0:
        return 0

    tips_median = statistics.median(tips)
    return math.ceil(tips_median)
