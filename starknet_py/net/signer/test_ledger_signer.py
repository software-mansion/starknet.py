import pytest

from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.ledger_signer import EIP_2645_PATH_LENGTH, LedgerSigner


def test_init_ledger_signer_with_invalid_derivation_path():
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
