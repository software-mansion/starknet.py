import pytest

from starknet_py.common import create_compiled_contract
from starknet_py.constants import EIP_2645_PATH_LENGTH
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import DeclareV1, DeployAccountV1, InvokeV1, StarknetChainId
from starknet_py.net.signer.ledger_signer import LedgerSigner
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
@pytest.mark.skip(reason="Interactive ledger signing is not implemented yet.")
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
