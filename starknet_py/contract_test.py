import pytest

from starknet_py.contract import Contract, DeclareResult, DeployResult
from starknet_py.net.account.base_account import BaseAccount


def test_compute_hash(balance_contract):
    assert (
        Contract.compute_contract_hash(balance_contract)
        == 0x12177EA61E5791CC068D7EE979B74F60A7205A23404C07440F4892B826147C0
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


@pytest.mark.parametrize("param", ["_account", "class_hash", "compiled_contract"])
def test_declare_result_post_init(param, account):
    kwargs = {
        "_account": account,
        "class_hash": 0,
        "compiled_contract": "",
    }
    del kwargs[param]

    with pytest.raises(ValueError, match=f"Argument {param} can't be None."):
        _ = DeclareResult(hash=0, _client=account.client, **kwargs)


def test_deploy_result_post_init(client):
    with pytest.raises(ValueError, match="Argument deployed_contract can't be None."):
        _ = DeployResult(
            hash=0,
            _client=client,
        )


def test_contract_raises_on_incorrect_provider_type():
    with pytest.raises(ValueError, match="Argument provider is not of accepted type."):
        Contract(address=0x1, abi=[], provider=1)  # pyright: ignore


def test_contract_create_with_base_account(account):
    contract = Contract(address=0x1, abi=[], provider=account)
    assert isinstance(contract.account, BaseAccount)
    assert contract.account == account
    assert contract.client == account.client


def test_contract_create_with_client(client):
    contract = Contract(address=0x1, abi=[], provider=client)
    assert contract.account is None
    assert contract.client == client


def test_throws_on_wrong_abi(account):
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
            provider=account,
            cairo_version=1,
        )
