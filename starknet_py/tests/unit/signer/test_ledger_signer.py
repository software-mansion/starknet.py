from sys import platform
from unittest.mock import MagicMock, Mock

import pytest

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import DeclareV3, DeployAccountV3, InvokeV3, StarknetChainId
from starknet_py.net.signer.ledger_signer import BlindSigningModeWarning
from starknet_py.tests.e2e.fixtures.accounts import mint_token_on_devnet
from starknet_py.tests.e2e.fixtures.constants import (
    MAX_RESOURCE_BOUNDS_SEPOLIA,
    STRK_FEE_CONTRACT_ADDRESS,
)

LEDGER_ACCOUNT_ADDRESS_SEPOLIA = (
    0x07D2B5E579BB434976E352811D4C3A9DAD7F5966AC2BED4FBBFB7A3B1A0E90DE
)


@pytest.mark.parametrize(
    "transaction",
    [
        InvokeV3(
            version=3,
            signature=[],
            nonce=1,
            resource_bounds=MAX_RESOURCE_BOUNDS_SEPOLIA,
            calldata=[
                1,
                2009894490435840142178314390393166646092438090257831307886760648929397478285,
                232670485425082704932579856502088130646006032362877466777181098476241604910,
                3,
                0x123,
                100,
                0,
            ],
            sender_address=0x123,
            tip=0,
        ),
        DeployAccountV3(
            class_hash=0x123,
            contract_address_salt=0x123,
            constructor_calldata=[1, 2, 3],
            version=3,
            signature=[],
            nonce=0,
            resource_bounds=MAX_RESOURCE_BOUNDS_SEPOLIA,
            tip=0,
        ),
    ],
)
# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
def test_clear_sign_transaction(transaction):
    # pylint: disable=redefined-outer-name, unused-import, import-outside-toplevel
    # docs: start
    from starknet_py.net.signer.ledger_signer import LedgerSigner, LedgerSigningMode

    # Create a `LedgerSigner` instance and pass chain id
    signer = LedgerSigner(
        chain_id=StarknetChainId.SEPOLIA,
    )

    # Sign the transaction
    signature = signer.sign_transaction(transaction)
    # docs: end

    assert isinstance(signature, list)
    assert len(signature) == 2
    assert all(isinstance(i, int) for i in signature)
    assert all(i != 0 for i in signature)


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
def test_blind_sign_transaction(transaction):
    # pylint: disable=import-outside-toplevel
    from starknet_py.net.signer.ledger_signer import LedgerSigner, LedgerSigningMode

    signer = LedgerSigner(
        chain_id=StarknetChainId.SEPOLIA,
    )
    # docs: start

    # Ledger also allows to blind sign transactions, but keep in mind that blind signing
    # is not recommended. It's unsafe because it lets you approve transactions or
    # messages without seeing their full contents.
    # ⚠️ Use blind signing at your own risk
    signer.signing_mode = LedgerSigningMode.BLIND
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
def test_blind_sign_warning():
    # pylint: disable=import-outside-toplevel, redefined-outer-name
    from starknet_py.net.signer.ledger_signer import LedgerSigner, LedgerSigningMode

    signer = LedgerSigner(
        chain_id=StarknetChainId.SEPOLIA,
    )
    signer.signing_mode = LedgerSigningMode.BLIND

    pattern = (
        "Signing in blind mode is not recommended. It prevents you from verifying "
        "the contents and leaving you vulnerable to unknowingly authorizing malicious transactions. "
        "⚠️ Use at your own risk"
    )
    tx = InvokeV3(
        version=3,
        signature=[],
        nonce=1,
        resource_bounds=MAX_RESOURCE_BOUNDS_SEPOLIA,
        calldata=[
            1,
            2009894490435840142178314390393166646092438090257831307886760648929397478285,
            232670485425082704932579856502088130646006032362877466777181098476241604910,
            3,
            0x123,
            100,
            0,
        ],
        sender_address=0x123,
        tip=0,
    )
    with pytest.warns(BlindSigningModeWarning, match=pattern):
        signer.sign_transaction(tx)


# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
def test_create_account_with_ledger_signer():
    # pylint: disable=unused-variable, import-outside-toplevel, redefined-outer-name, reimported
    from starknet_py.net.account.account import Account
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.signer.ledger_signer import LedgerSigner

    signer = LedgerSigner(
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
async def test_deploy_account_and_transfer(client):
    # pylint: disable=import-outside-toplevel, reimported, redefined-outer-name, too-many-locals
    # docs-deploy-account-and-transfer: start
    from starknet_py.contract import Contract
    from starknet_py.hash.address import compute_address
    from starknet_py.net.account.account import Account
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.signer.ledger_signer import LedgerSigner

    rpc_client = FullNodeClient(node_url="https://your.node.url")
    # docs-deploy-account-and-transfer: end
    rpc_client = client
    # docs-deploy-account-and-transfer: start
    signer = LedgerSigner(
        chain_id=StarknetChainId.SEPOLIA,
    )
    # argent v0.4.0 class hash
    class_hash = 0x36078334509B514626504EDC9FB252328D1A240E4E948BEF8D0C08DFF45927F
    salt = 1
    calldata = [0, signer.public_key, 1]
    address = compute_address(
        salt=salt,
        class_hash=class_hash,
        constructor_calldata=calldata,
    )
    account = Account(
        address=address,
        client=rpc_client,
        signer=signer,
        chain=StarknetChainId.SEPOLIA,
    )

    # Remember to prefund the account
    # docs-deploy-account-and-transfer: end
    # Here we prefund the devnet account for test purposes
    await mint_token_on_devnet(
        url=rpc_client.url.replace("/rpc", ""),
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

    await rpc_client.deploy_account(signed_tx)

    recipient_address = 0x123
    # docs-deploy-account-and-transfer: end
    recipient_balance_before = (
        await _get_account_balance_strk(rpc_client, recipient_address)
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
        await _get_account_balance_strk(rpc_client, recipient_address)
    )[0]

    assert recipient_balance_before + 100 == recipient_balance_after


@pytest.mark.asyncio
# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
async def test_invoke_v3_long_calldata(client_fork_mode):
    # pylint: disable=import-outside-toplevel, redefined-outer-name, reimported
    from starknet_py.contract import Contract
    from starknet_py.net.account.account import Account
    from starknet_py.net.signer.ledger_signer import LedgerSigner

    # Contract deployed on Sepolia
    contract_address = (
        0x042C25F2DD9C4AA010E7A4ADA1BFB1C99E5DBEA2850C59D8FD9F59F554CC268E
    )

    signer = LedgerSigner(
        chain_id=StarknetChainId.SEPOLIA,
    )

    account = Account(
        address=LEDGER_ACCOUNT_ADDRESS_SEPOLIA,
        client=client_fork_mode,
        signer=signer,
        chain=StarknetChainId.SEPOLIA,
    )

    contract = await Contract.from_address(provider=account, address=contract_address)

    # `fn_with_many_args` accepts 17 arguments
    args = list(range(1, 18))

    invocation = await contract.functions["fn_with_many_args"].invoke_v3(
        *args,
        auto_estimate=True,
    )
    await invocation.wait_for_acceptance()


@pytest.mark.asyncio
# TODO (#1425): Currently Ledger tests are skipped on Windows due to different Speculos setup.
@pytest.mark.skipif(
    platform == "win32",
    reason="Testing Ledger is skipped on Windows due to different Speculos setup.",
)
async def test_deploy_account_v3_long_calldata(client_fork_mode):
    # pylint: disable=import-outside-toplevel, redefined-outer-name, reimported
    from starknet_py.contract import Contract
    from starknet_py.net.account.account import Account
    from starknet_py.net.signer.ledger_signer import LedgerSigner

    # Contract declared on Sepolia
    class_hash = 0x040ACE4954F5F7D8BF202A87EAD2AD4BA77F245740A35DD11AFD6912DEB08ABF

    signer = LedgerSigner(
        chain_id=StarknetChainId.SEPOLIA,
    )

    account = Account(
        address=LEDGER_ACCOUNT_ADDRESS_SEPOLIA,
        client=client_fork_mode,
        signer=signer,
        chain=StarknetChainId.SEPOLIA,
    )

    # constructor accepts 17 arguments
    constructor_args = list(range(1, 18))

    deploy_result = await Contract.deploy_contract_v3(
        account=account,
        class_hash=class_hash,
        constructor_args=constructor_args,
        auto_estimate=True,
    )
    await deploy_result.wait_for_acceptance()
