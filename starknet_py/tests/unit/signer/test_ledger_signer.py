from sys import platform
from unittest.mock import MagicMock, Mock

import pytest

from starknet_py.constants import EIP_2645_PATH_LENGTH
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import DeclareV3, DeployAccountV3, InvokeV3, StarknetChainId
from starknet_py.net.signer.ledger_signer import LedgerSigner
from starknet_py.tests.e2e.fixtures.accounts import mint_token_on_devnet
from starknet_py.tests.e2e.fixtures.constants import STRK_FEE_CONTRACT_ADDRESS


# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
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


@pytest.mark.parametrize(
    "transaction",
    [
        Mock(spec=InvokeV3, calculate_hash=MagicMock(return_value=111)),
        Mock(spec=DeployAccountV3, calculate_hash=MagicMock(return_value=222)),
        Mock(spec=DeclareV3, calculate_hash=MagicMock(return_value=333)),
    ],
)
# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
def test_sign_transaction(transaction):
    # docs: start

    # Create a `LedgerSigner` instance with the derivation path and chain id
    signer = LedgerSigner(
        derivation_path_str="m/2645'/1195502025'/1470455285'/0'/0'/0",
        chain_id=StarknetChainId.SEPOLIA,
    )

    # Sign the transaction
    signature = signer.sign_transaction(transaction)
    # docs: end

    assert isinstance(signature, list)
    assert len(signature) == 2
    assert all(isinstance(i, int) for i in signature)
    assert all(i != 0 for i in signature)


# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
def test_create_account_with_ledger_signer():
    # pylint: disable=unused-variable
    signer = LedgerSigner(
        derivation_path_str="m/2645'/1195502025'/1470455285'/0'/0'/0",
        chain_id=StarknetChainId.SEPOLIA,
    )

    # docs: start

    client = FullNodeClient(node_url="https://your.node.url")
    # Create an `Account` instance with the ledger signer
    account = Account(
        client=client,
        address=0x1111,
        signer=signer,
        chain=StarknetChainId.SEPOLIA,
    )
    # Now you can use Account as you'd always do
    # docs: end


async def _get_account_balance_strk(client: FullNodeClient, address: int):
    balance = await client.call_contract(
        call=Call(
            to_addr=int(STRK_FEE_CONTRACT_ADDRESS, 16),
            calldata=[address],
            selector=get_selector_from_name("balanceOf"),
        )
    )
    return balance


@pytest.mark.asyncio
# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
@pytest.mark.skip("TODO(#1560): Fix this test, class hash used here is not deployed")
async def test_deploy_account_and_transfer(client):
    signer = LedgerSigner(
        derivation_path_str="m/2645'/1195502025'/1470455285'/0'/0'/0",
        chain_id=StarknetChainId.SEPOLIA,
    )
    # docs-deploy-account-and-transfer: start
    class_hash = 0x61DAC032F228ABEF9C6626F995015233097AE253A7F72D68552DB02F2971B8F
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

    # Remember to prefund the account
    # docs-deploy-account-and-transfer: end
    # Here we prefund the devnet account for test purposes
    await mint_token_on_devnet(
        url=client.url.replace("/rpc", ""),
        address=address,
        amount=5000000000000000000000,
        unit="FRI",
    )
    # docs-deploy-account-and-transfer: start
    signed_tx = await account.sign_deploy_account_v3(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=calldata,
        auto_estimate=True,
    )

    await client.deploy_account(signed_tx)

    recipient_address = (
        0x1323CACBC02B4AAED9BB6B24D121FB712D8946376040990F2F2FA0DCF17BB5B
    )
    # docs-deploy-account-and-transfer: end
    recipient_balance_before = (
        await _get_account_balance_strk(client, recipient_address)
    )[0]
    # docs-deploy-account-and-transfer: start
    contract = await Contract.from_address(
        provider=account, address=STRK_FEE_CONTRACT_ADDRESS
    )
    invocation = await contract.functions["transfer"].invoke_v3(
        recipient_address, 100, auto_estimate=True
    )
    await invocation.wait_for_acceptance()
    # docs-deploy-account-and-transfer: end
    recipient_balance_after = (
        await _get_account_balance_strk(client, recipient_address)
    )[0]

    assert recipient_balance_before + 100 == recipient_balance_after
