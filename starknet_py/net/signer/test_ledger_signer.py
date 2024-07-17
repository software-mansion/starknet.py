import pytest

from starknet_py.net.signer.ledger_signer import LedgerSigner, EIP_2645_PATH_LENGTH


def test_init_ledger_signer_with_invalid_derivation_path():
    with pytest.raises(ValueError, match="Empty derivation path"):
        LedgerSigner("")

    with pytest.raises(ValueError, match=fr"Derivation path is not {EIP_2645_PATH_LENGTH}-level long"):
        LedgerSigner("m/44'/60'/0'/0/0")

    with pytest.raises(ValueError, match=r"Derivation path is not prefixed with m/2645."):
        LedgerSigner("m/44'/60'/0'/0/0/0")
