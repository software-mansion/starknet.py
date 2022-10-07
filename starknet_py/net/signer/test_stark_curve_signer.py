import pytest

from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import InvokeFunction, DeployAccount
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner, KeyPair


@pytest.mark.parametrize(
    "transaction",
    [
        InvokeFunction(
            contract_address=0x1,
            calldata=[1, 2, 3],
            max_fee=10000,
            signature=[],
            nonce=23,
            version=1,
        ),
        DeployAccount(
            class_hash=0x1,
            contract_address_salt=0x2,
            constructor_calldata=[1, 2, 3, 4],
            max_fee=10000,
            signature=[],
            nonce=23,
            version=1,
        ),
    ],
)
def test_sign_transaction(transaction):
    signer = StarkCurveSigner(
        account_address=0x1,
        key_pair=KeyPair.from_private_key(0x1),
        chain_id=StarknetChainId.TESTNET,
    )

    signature = signer.sign_transaction(transaction)

    assert isinstance(signature, list)
    assert len(signature) > 0
    assert all(isinstance(i, int) for i in signature)
    assert all(i != 0 for i in signature)
