from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import compute_invoke_hash


def test_invoke_hash():
    for selector in [
        "increase_balance",
        1530486729947006463063166157847785599120665941190480211966374137237989315360,
    ]:
        assert (
            compute_invoke_hash(
                entry_point_selector=selector,
                contract_address=0x03606DB92E563E41F4A590BC01C243E8178E9BA8C980F8E464579F862DA3537C,
                calldata=[1234],
                chain_id=StarknetChainId.TESTNET,
                version=0,
                max_fee=0,
            )
            == 0xD0A52D6E77B836613B9F709AD7F4A88297697FEFBEF1ADA3C59692FF46702C
        )
