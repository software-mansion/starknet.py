import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeclareV3, DeployAccountV1, InvokeV1
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.fixtures.misc import load_contract

compiled_contract = load_contract("HelloStarknet")["sierra"]
sierra_contract_class = create_sierra_compiled_contract(compiled_contract)


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
        DeclareV3(
            contract_class=sierra_contract_class,
            compiled_class_hash=0x1,
            sender_address=0x123,
            signature=[],
            nonce=4,
            version=3,
            resource_bounds=MAX_RESOURCE_BOUNDS,
        ),
    ],
)
def test_sign_transaction(transaction):
    signer = StarkCurveSigner(
        account_address=0x1,
        key_pair=KeyPair.from_private_key(0x1),
        chain_id=StarknetChainId.MAINNET,
    )

    signature = signer.sign_transaction(transaction)

    assert isinstance(signature, list)
    assert len(signature) > 0
    assert all(isinstance(i, int) for i in signature)
    assert all(i != 0 for i in signature)


def test_key_pair():
    key_pair = KeyPair(public_key="0x123", private_key="0x456")

    assert isinstance(key_pair.public_key, int)
    assert isinstance(key_pair.private_key, int)

    key_pair = KeyPair.from_private_key("0x789")

    assert isinstance(key_pair.public_key, int)
    assert isinstance(key_pair.private_key, int)
