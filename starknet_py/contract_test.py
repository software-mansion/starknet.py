import pytest

from starknet_py.contract import Contract, DeclareResult, DeployResult
from starknet_py.net.account._account_proxy import AccountProxy
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_DIR

SOURCE = """
// Declare this file as a StarkNet contract and set the required
// builtins.
%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

// Define a storage variable.
@storage_var
func balance() -> (res: felt) {
}

// Increases the balance by the given amount.
@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    let (res) = balance.read();
    balance.write(res + amount);
    return ();
}

// Returns the current balance.
@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: felt, b: felt
) {
    return ();
}
"""

SOURCE_WITH_IMPORTS = """
%lang starknet
%builtins pedersen range_check

from inner.inner import MockStruct

@external
func put{syscall_ptr: felt*, pedersen_ptr, range_check_ptr}(key: felt, value: felt) {
    return ();
}
"""

EXPECTED_HASH = (
    503253050526186908280124384407865038867585652783408167932765780369167667415
)


EXPECTED_HASH_WITH_IMPORTS = (
    261412312091196127884045926298824262716023266111934769893960173054947391504
)

EXPECTED_ADDRESS = (
    189023603034557919684596652904755695539249539924658863620932079547695762912
)

EXPECTED_ADDRESS_WITH_IMPORTS = (
    1265406736018442209950241864397668901077908617314293391280948790921629758434
)

search_path = CONTRACTS_DIR


def test_compute_hash():
    assert Contract.compute_contract_hash(SOURCE) == EXPECTED_HASH


def test_compute_hash_with_search_path():
    assert (
        Contract.compute_contract_hash(
            SOURCE_WITH_IMPORTS, search_paths=[str(search_path)]
        )
        == EXPECTED_HASH_WITH_IMPORTS
    )


def test_compute_address():
    assert (
        Contract.compute_address(
            compilation_source=SOURCE, constructor_args=[21, 37], salt=1111
        )
        == EXPECTED_ADDRESS
    )


def test_compute_address_with_imports():
    assert (
        Contract.compute_address(
            compilation_source=SOURCE_WITH_IMPORTS,
            salt=1111,
            search_paths=[str(search_path)],
        )
        == EXPECTED_ADDRESS_WITH_IMPORTS
    )


def test_compute_address_throws_on_no_source():
    with pytest.raises(
        ValueError, match="One of compiled_contract or compilation_source is required."
    ):
        Contract.compute_address(salt=1111)


def test_no_valid_source():
    with pytest.raises(
        ValueError, match="One of compiled_contract or compilation_source is required."
    ):
        Contract.compute_contract_hash()


@pytest.mark.parametrize("param", ["_account", "class_hash", "compiled_contract"])
def test_declare_result_post_init(param, new_gateway_account_client):
    kwargs = {
        "_account": new_gateway_account_client,
        "class_hash": 0,
        "compiled_contract": "",
    }
    del kwargs[param]

    with pytest.raises(ValueError, match=f"Argument {param} can't be None."):
        _ = DeclareResult(hash=0, _client=new_gateway_account_client.client, **kwargs)


def test_deploy_result_post_init(gateway_client):
    with pytest.raises(ValueError, match="Argument deployed_contract can't be None."):
        _ = DeployResult(
            hash=0,
            _client=gateway_client,
        )


def test_contract_raises_on_no_provider_and_client():
    with pytest.raises(ValueError, match="One of provider or client must be provided."):
        Contract(address=1234, abi=[])


def test_contract_raises_on_both_provider_and_client(
    gateway_account_client, gateway_client
):
    with pytest.raises(
        ValueError, match="Arguments provider and client are mutually exclusive."
    ):
        Contract(
            address=1234, abi=[], provider=gateway_account_client, client=gateway_client
        )


def test_contract_raises_on_incorrect_provider_type():
    with pytest.raises(ValueError, match="Argument provider is not of accepted type."):
        Contract(address=0x1, abi=[], provider=1)  # pyright: ignore


def test_contract_create_with_base_account(gateway_account):
    contract = Contract(address=0x1, abi=[], provider=gateway_account)
    assert isinstance(contract.account, BaseAccount)
    assert contract.account == gateway_account
    assert contract.client == gateway_account.client


def test_contract_create_with_account_client(gateway_account_client):
    contract = Contract(address=0x1, abi=[], provider=gateway_account_client)
    assert isinstance(contract.account, AccountProxy)
    assert contract.client == gateway_account_client.client

    contract = Contract(address=0x1, abi=[], client=gateway_account_client)
    assert isinstance(contract.account, AccountProxy)
    assert contract.client == gateway_account_client.client


def test_contract_create_with_client(gateway_client):
    contract = Contract(address=0x1, abi=[], provider=gateway_client)
    assert contract.account is None
    assert contract.client == gateway_client

    contract = Contract(address=0x1, abi=[], client=gateway_client)
    assert contract.account is None
    assert contract.client == gateway_client
