from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import compute_invoke_hash, compute_deploy_hash

ADDRESS = 0x03606DB92E563E41F4A590BC01C243E8178E9BA8C980F8E464579F862DA3537C


def test_invoke_hash():
    for selector in [
        "increase_balance",
        1530486729947006463063166157847785599120665941190480211966374137237989315360,
    ]:
        assert (
            compute_invoke_hash(
                entry_point_selector=selector,
                contract_address=ADDRESS,
                calldata=[1234],
                chain_id=StarknetChainId.TESTNET,
            )
            == 0x203BFF8307C3266B0749A0D1DBA143907F32F7E55C84A4A34077690C9C91BAC
        )


def test_deploy_hash():
    assert (
        compute_deploy_hash(
            contract_address=ADDRESS,
            calldata=[],
            chain_id=StarknetChainId.TESTNET,
        )
        == 0x341380BA58BF69F567E876C576D4CFFCB4D4374F0C63C025D120253426F013E
    )
