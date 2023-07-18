import pytest

from starknet_py.contract import Contract, DeployResult
from starknet_py.net.account.base_account import BaseAccount


def test_compute_hash(balance_contract):
    assert (
        Contract.compute_contract_hash(balance_contract)
        == 0xF6C57433D98D26B9ADD810EFFADD20FAC9C9E716EFC882E509CD016D3A1C71
    )


def test_compute_address(constructor_with_arguments_compiled):
    assert (
        Contract.compute_address(
            compiled_contract=constructor_with_arguments_compiled,
            constructor_args=[
                10,
                (1, (2, 3)),
                [1, 2, 3],
                {"value": 12, "nested_struct": {"value": 99}},
            ],
            salt=1111,
        )
        > 0
    )


def test_deploy_result_post_init(client):
    with pytest.raises(ValueError, match="Argument deployed_contract can't be None."):
        _ = DeployResult(
            hash=0,
            _client=client,
        )


def test_contract_raises_on_incorrect_provider_type():
    with pytest.raises(ValueError, match="Argument provider is not of accepted type."):
        Contract(address=0x1, abi=[], provider=1)  # pyright: ignore


def test_contract_create_with_base_account(mock_account):
    contract = Contract(address=0x1, abi=[], provider=mock_account)
    assert isinstance(contract.account, BaseAccount)
    assert contract.account == mock_account
    assert contract.client == mock_account.client


def test_contract_create_with_client(client):
    contract = Contract(address=0x1, abi=[], provider=client)
    assert contract.account is None
    assert contract.client == client


def test_throws_on_wrong_abi(mock_account):
    with pytest.raises(
        ValueError, match="Make sure valid ABI is used to create a Contract instance"
    ):
        Contract(
            address=0x1,
            abi=[
                {
                    "type": "function",
                    "name": "empty",
                    "inputs": "",  # inputs should be a list
                }
            ],
            provider=mock_account,
            cairo_version=1,
        )
