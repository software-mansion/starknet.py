import math
import statistics
from typing import Optional, Union

from starknet_py.net.client import Client
from starknet_py.net.client_models import Hash, LatestTag, StarknetBlock, TransactionV3
from starknet_py.net.client_utils import get_block_identifier


async def get_tips_median(
    client: Client,
    block_hash: Optional[Union[Hash, LatestTag]] = None,
    block_number: Optional[Union[int, LatestTag]] = None,
) -> int:
    """
    Get a median of tips for the provided block.

    Does not support `pre_confirmed` block.

    :param client: Client instance.
    :param block_hash: Block's hash or literal `"latest"`
    :param block_number: Block's number or literal `"latest"`
    """
    # Raise error if a pre_confirmed block is used.
    get_block_identifier(
        block_hash=block_hash,
        block_number=block_number,
        allow_pre_confirmed=False,
    )

    block_with_txs = await client.get_block_with_txs(block_hash, block_number)
    assert isinstance(block_with_txs, StarknetBlock)

    tips = []
    for tx in block_with_txs.transactions:
        if isinstance(tx, TransactionV3):
            tips.append(tx.tip)

    if len(tips) == 0:
        return 0

    tips_median = statistics.median(tips)
    return math.ceil(tips_median)
