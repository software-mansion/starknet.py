import dataclasses
from typing import List

import pytest_asyncio

from starknet_py.common import create_compiled_contract
from starknet_py.net.client_models import Declare
from starknet_py.tests.e2e.utils import MAX_FEE


@pytest_asyncio.fixture()
async def declare_transactions(
    new_gateway_account_client, map_compiled_contract, erc20_compiled_contract
) -> List[Declare]:
    """
    Returns a list of declare transactions
    """
    declare_tx_map = await new_gateway_account_client.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )

    compiled_contract = create_compiled_contract(
        compiled_contract=erc20_compiled_contract
    )
    declare_tx_erc20 = Declare(
        contract_class=compiled_contract,
        sender_address=new_gateway_account_client.address,
        max_fee=0,
        signature=[],
        nonce=declare_tx_map.nonce + 1,
        version=new_gateway_account_client.supported_tx_version,
    )
    max_fee = await new_gateway_account_client._get_max_fee(  # pylint: disable=protected-access
        transaction=declare_tx_erc20, max_fee=MAX_FEE
    )
    declare_tx_erc20 = dataclasses.replace(declare_tx_erc20, max_fee=max_fee)
    signature = new_gateway_account_client.signer.sign_transaction(declare_tx_erc20)
    dataclasses.replace(declare_tx_erc20, signature=signature)

    return [declare_tx_map, declare_tx_erc20]
