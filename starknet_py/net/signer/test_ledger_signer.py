import pytest

from starknet_py.common import create_compiled_contract
from starknet_py.constants import EIP_2645_PATH_LENGTH
from starknet_py.hash.address import compute_address
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import DeclareV1, DeployAccountV1, InvokeV1, StarknetChainId
from starknet_py.net.signer.ledger_signer import LedgerSigner
from starknet_py.tests.e2e.fixtures.accounts import mint_token_on_devnet
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V0_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


def test_init_with_invalid_derivation_path():
    with pytest.raises(ValueError, match="Empty derivation path"):
        LedgerSigner(derivation_path_str="", chain_id=StarknetChainId.SEPOLIA)

    with pytest.raises(
        ValueError, match=rf"Derivation path is not {EIP_2645_PATH_LENGTH}-level long"
    ):
        LedgerSigner(
            derivation_path_str="m/2645'/1195502025'/1470455285'/0'/0'/0/0",
            chain_id=StarknetChainId.SEPOLIA,
        )

    with pytest.raises(
        ValueError, match=r"Derivation path is not prefixed with m/2645."
    ):
        LedgerSigner(
            derivation_path_str="m/1234'/1195502025'/1470455285'/0'/0'/0",
            chain_id=StarknetChainId.SEPOLIA,
        )


compiled_contract = read_contract(
    "erc20_compiled.json", directory=CONTRACTS_COMPILED_V0_DIR
)


@pytest.mark.parametrize(
    "transaction",
    [
        InvokeV1(
            sender_address=0x1,
            calldata=[1, 2, 3],
            max_fee=10000,
            signature=[],
            nonce=23,
            version=1,
        ),
        DeployAccountV1(
            class_hash=0x1,
            contract_address_salt=0x2,
            constructor_calldata=[1, 2, 3, 4],
            max_fee=10000,
            signature=[],
            nonce=23,
            version=1,
        ),
        DeclareV1(
            contract_class=create_compiled_contract(
                compiled_contract=compiled_contract
            ),
            sender_address=123,
            max_fee=10000,
            signature=[],
            nonce=23,
            version=1,
        ),
    ],
)
def test_sign_transaction(transaction):
    signer = LedgerSigner(
        derivation_path_str="m/2645'/1195502025'/1470455285'/0'/0'/0",
        chain_id=StarknetChainId.MAINNET,
    )

    signature = signer.sign_transaction(transaction)

    assert isinstance(signature, list)
    assert len(signature) > 0
    assert all(isinstance(i, int) for i in signature)
    assert all(i != 0 for i in signature)


async def _get_account_balance_eth(client: FullNodeClient, address: int):
    eth_address = int(
        "0x49D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7", 16
    )
    balance = await client.call_contract(
        call=Call(
            to_addr=eth_address,
            calldata=[address],
            selector=get_selector_from_name("balanceOf"),
        )
    )
    return balance


@pytest.mark.asyncio
async def test_deploy_account_and_transfer(client):
    signer = LedgerSigner(
        derivation_path_str="m/2645'/1195502025'/1470455285'/0'/0'/0",
        chain_id=StarknetChainId.SEPOLIA,
    )

    class_hash = 0x61dac032f228abef9c6626f995015233097ae253a7f72d68552db02f2971b8f

    salt = 1
    calldata = [signer.public_key]
    address = compute_address(
        salt=salt,
        class_hash=class_hash,
        constructor_calldata=calldata,
    )
    account = Account(
        address=address,
        client=client,
        signer=signer,
        chain=StarknetChainId.SEPOLIA,
    )
    await mint_token_on_devnet(
        url=client.url.replace("/rpc", ""),
        address=address,
        amount=5000000000000000000000,
        unit="WEI",
    )

    signed_tx = await account.sign_deploy_account_v1(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=calldata,
        auto_estimate=True,
    )

    await client.deploy_account(signed_tx)

    recipient_address = 0x1323cacbc02b4aaed9bb6b24d121fb712d8946376040990f2f2fa0dcf17bb5b
    sender_balance_before = (await _get_account_balance_eth(client, address))[0]
    recipient_balance_before = (
        await _get_account_balance_eth(client, recipient_address)
    )[0]

    eth_address = int(
        "0x49D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7", 16
    )

    call = Call(
        to_addr=eth_address,
        calldata=[recipient_address, 100, 0],
        selector=get_selector_from_name("transfer"),
    )

    await account.execute_v1(call, auto_estimate=True)

    sender_balance_after = (await _get_account_balance_eth(client, address))[0]
    recipient_balance_after = (
        await _get_account_balance_eth(client, recipient_address)
    )[0]
    print(f"Balance of {address} after: {sender_balance_after}")
    print(f"Balance of {recipient_address} after: {recipient_balance_after}")

    assert recipient_balance_before + 100 == recipient_balance_after
