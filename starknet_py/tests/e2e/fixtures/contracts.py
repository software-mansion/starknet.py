# pylint: disable=redefined-outer-name

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.tests.e2e.fixtures.constants import STRK_FEE_CONTRACT_ADDRESS


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
