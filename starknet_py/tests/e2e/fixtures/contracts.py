# pylint: disable=redefined-outer-name
from typing import List

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE, STRK_FEE_CONTRACT_ADDRESS


async def deploy_contract(account: BaseAccount, class_hash: int, abi: List) -> Contract:
    """
    Deploys a contract and returns its instance.
    """
    deployment_result = await Contract.deploy_contract_v1(
        account=account, class_hash=class_hash, abi=abi, max_fee=MAX_FEE
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


@pytest.fixture(scope="package")
def eth_fee_contract(account: BaseAccount, cairo_0_fee_contract_abi) -> Contract:
    """
    Returns an instance of the ETH fee contract. It is used to transfer tokens.
    """

    return Contract(
        address=FEE_CONTRACT_ADDRESS,
        abi=cairo_0_fee_contract_abi,
        provider=account,
        cairo_version=0,
    )


@pytest.fixture(scope="package")
def strk_fee_contract(account: BaseAccount, cairo_0_fee_contract_abi) -> Contract:
    """
    Returns an instance of the STRK fee contract. It is used to transfer tokens.
    """

    return Contract(
        address=STRK_FEE_CONTRACT_ADDRESS,
        abi=cairo_0_fee_contract_abi,
        provider=account,
        cairo_version=0,
    )


@pytest.fixture(scope="package")
def cairo_0_fee_contract_abi():
    return [
        {
            "inputs": [
                {"name": "recipient", "type": "felt"},
                {"name": "amount", "type": "Uint256"},
            ],
            "name": "transfer",
            "outputs": [{"name": "success", "type": "felt"}],
            "type": "function",
        },
        {
            "members": [
                {"name": "low", "offset": 0, "type": "felt"},
                {"name": "high", "offset": 1, "type": "felt"},
            ],
            "name": "Uint256",
            "size": 2,
            "type": "struct",
        },
    ]
