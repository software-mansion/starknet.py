import math
import statistics
from typing import Optional, Union

from starknet_py.net.client import Client
from starknet_py.net.client_models import Hash, LatestTag, TransactionV3


async def get_tips_median(
    client: Client,
    block_hash: Optional[Union[Hash, LatestTag]] = None,
    block_number: Optional[Union[int, LatestTag]] = None,
) -> int:
    """
    Get a median of tips for the provided block.
    If no block is provided, the `pre-confirmed` block is used.

    :param client: Client instance.
    :param block_hash: Block's hash or literal `"latest"`
    :param block_number: Block's number or literal `"latest"`
    """
    if block_hash is None and block_number is None:
        block_hash = "pre_confirmed"

    block_with_txs = await client.get_block_with_txs(block_hash, block_number)

    tips = []
    for tx in block_with_txs.transactions:
        if isinstance(tx, TransactionV3):
            tips.append(tx.tip)

    if len(tips) == 0:
        return 0

    tips_median = statistics.median(tips)
    return math.ceil(tips_median)
