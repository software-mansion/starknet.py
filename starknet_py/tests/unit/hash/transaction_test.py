import pytest

from starknet_py.hash.transaction import (
    CommonTransactionV3Fields,
    TransactionHashPrefix,
    compute_declare_v2_transaction_hash,
    compute_declare_v3_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_deploy_account_v3_transaction_hash,
    compute_invoke_transaction_hash,
    compute_invoke_v3_transaction_hash,
    compute_transaction_hash,
)
from starknet_py.net.client_models import DAMode, ResourceBounds, ResourceBoundsMapping
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            [TransactionHashPrefix.INVOKE, 2, 3, 4, [5], 6, 7, [8]],
            1176541524183318710439453346174486593835028723304878846501762065493748312757,
        ),
        (
            [TransactionHashPrefix.L1_HANDLER, 15, 39, 74, [74], 39, 15, [28]],
            1226653506056503634668815848352741482067480791322607584496401451909331743178,
        ),
        (
            [
                TransactionHashPrefix.INVOKE,
                0x0,
                0x2A,
                0x64,
                [],
                0x0,
                0x534E5F474F45524C49,
            ],
            0x7D260744DE9D8C55E7675A34512D1951A7B262C79E685D26599EDD2948DE959,
        ),
    ),
)
def test_compute_transaction_hash(data, expected_hash):
    assert compute_transaction_hash(*data) == expected_hash


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            {
                "contract_address": 2,
                "class_hash": 3,
                "constructor_calldata": [4],
                "salt": 5,
                "version": 6,
                "max_fee": 7,
                "chain_id": 8,
                "nonce": 9,
            },
            0x6199E956E541CBB06589C4A63C2578A8ED6B697C0FA35B002F48923DFE648EE,
        ),
    ),
)
def test_compute_deploy_account_transaction_hash(data, expected_hash):
    assert compute_deploy_account_transaction_hash(**data) == expected_hash


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            {
                "class_hash": 2,
                "sender_address": 3,
                "version": 4,
                "max_fee": 5,
                "chain_id": 6,
                "nonce": 7,
                "compiled_class_hash": 8,
            },
            0x67EA411072DD2EF3BA36D9680F040A02E599F80F4770E204ECBB2C47C226793,
        ),
    ),
)
def test_compute_declare_v2_transaction_hash(data, expected_hash):
    assert compute_declare_v2_transaction_hash(**data) == expected_hash


@pytest.mark.parametrize(
    "data, expected_hash",
    (
        (
            {
                "sender_address": 3,
                "version": 4,
                "calldata": [5],
                "max_fee": 6,
                "chain_id": 7,
                "nonce": 8,
            },
            0x505BBF7CD810531C53526631078DAA314BFD036C80C7C6E3A02C608DB8E31DE,
        ),
    ),
)
def test_compute_invoke_transaction_hash(data, expected_hash):
    assert compute_invoke_transaction_hash(**data) == expected_hash


@pytest.mark.parametrize(
    "common_data, declare_data, expected_hash",
    (
        (
            {
                "address": 0x52125C1E043126C637D1436D9551EF6C4F6E3E36945676BBD716A56E3A41B7A,
                "chain_id": 0x534E5F474F45524C49,
                "nonce": 0x675,
                "tip": 0x0,
                "paymaster_data": [],
                "nonce_data_availability_mode": DAMode.L1,
                "fee_data_availability_mode": DAMode.L1,
                "tx_prefix": TransactionHashPrefix.DECLARE,
                "version": 0x3,
            },
            {
                "class_hash": 0x2338634F11772EA342365ABD5BE9D9DC8A6F44F159AD782FDEBD3DB5D969738,
                "compiled_class_hash": 0x17B5169C770D0E49100AB0FC672A49CA90CC572F21F79A640B5227B19D3A447,
                "account_deployment_data": [],
            },
            0x16081C54C3BEDC5079E0024896BFD85ED7E57FFD52B138CBC73AF0F34C7FCCE,
        ),
    ),
)
def test_compute_declare_v3_transaction_hash(common_data, declare_data, expected_hash):
    assert (
        compute_declare_v3_transaction_hash(
            **declare_data,
            common_fields=CommonTransactionV3Fields(
                **common_data, resource_bounds=MAX_RESOURCE_BOUNDS
            ),
        )
        == expected_hash
    )


@pytest.mark.parametrize(
    "common_data, invoke_data, expected_hash",
    (
        (
            {
                "address": 0x35ACD6DD6C5045D18CA6D0192AF46B335A5402C02D41F46E4E77EA2C951D9A3,
                "chain_id": 0x534E5F474F45524C49,
                "nonce": 0x5,
                "tip": 0x0,
                "paymaster_data": [],
                "nonce_data_availability_mode": DAMode.L1,
                "fee_data_availability_mode": DAMode.L1,
                "tx_prefix": TransactionHashPrefix.INVOKE,
                "version": 0x3,
                "resource_bounds": MAX_RESOURCE_BOUNDS,
            },
            {
                "calldata": [
                    0x2,
                    0x6359ED638DF79B82F2F9DBF92ABBCB41B57F9DD91EAD86B1C85D2DEE192C,
                    0xB17D8A2731BA7CA1816631E6BE14F0FC1B8390422D649FA27F0FBB0C91EEA8,
                    0x0,
                    0x3FE8E4571772BBE0065E271686BD655EFD1365A5D6858981E582F82F2C10313,
                    0x2FD9126EE011F3A837CEA02E32AE4EE73342D827E216998E5616BAB88D8B7EA,
                    0x1,
                    0x2FD9126EE011F3A837CEA02E32AE4EE73342D827E216998E5616BAB88D8B7EA,
                ],
                "account_deployment_data": [],
            },
            0x119386B4AAAEF905BF027D3DD2734474C5E944942BF3FBD8FDB442704D32B8B,
        ),
        # Below transaction was submitted on integration network.
        (
            {
                "address": 0x7BFCD6BD5B220A1D46921D92924DDEC46BB7E49D05354C76A8714B41269B2F8,
                "chain_id": StarknetChainId.SEPOLIA_INTEGRATION,
                "nonce": 0x25,
                "tip": 0x0,
                "paymaster_data": [],
                "nonce_data_availability_mode": DAMode.L1,
                "fee_data_availability_mode": DAMode.L1,
                "tx_prefix": TransactionHashPrefix.INVOKE,
                "version": 0x3,
                "resource_bounds": ResourceBoundsMapping(
                    l1_gas=ResourceBounds(
                        max_amount=0x0, max_price_per_unit=0x15D3EF79800
                    ),
                    l2_gas=ResourceBounds(
                        max_amount=0x7757FAC, max_price_per_unit=0x2CB417800
                    ),
                    l1_data_gas=ResourceBounds(
                        max_amount=0xC0, max_price_per_unit=0x5DC
                    ),
                ),
            },
            {
                "calldata": [
                    0x1,
                    0x70A5DA4F557B77A9C54546E4BCC900806E28793D8E3EAAA207428D2387249B7,
                    0x31341177714D81AD9CCD0C903211BC056A60E8AF988D0FD918CC43874549653,
                    0x0,
                ],
                "account_deployment_data": [],
                "proof_facts": [
                    0x50524F4F4630,
                    0x5649525455414C5F534E4F53,
                    0x3E98C2D7703B03A7EDB73ED7F075F97F1DCBAA8F717CDF6E1A57BF058265473,
                    0x5649525455414C5F534E4F5330,
                    0x2256B2,
                    0x4272EA7D22D1B1E91D4D6EB1C55FCB5769B676DF746CF2FE77AF8FFFB86EEF2,
                    0x6989A681C469D769F3A706C56550A63741A4B2D32BEF4B1209A26DAAD1DBB6,
                    0x0,
                ],
            },
            0x7C173B8A109AB589694C89431E2C6070EA8662087B012F62081FAB6BACA4F6E,
        ),
    ),
)
def test_compute_invoke_v3_transaction_hash(common_data, invoke_data, expected_hash):
    assert (
        compute_invoke_v3_transaction_hash(
            **invoke_data,
            common_fields=CommonTransactionV3Fields(
                **common_data,
            ),
        )
        == expected_hash
    )


# TODO(#1498): Remove the skip mark
@pytest.mark.skip
@pytest.mark.parametrize(
    "common_data, deploy_account_data, expected_hash",
    (
        (
            {
                "address": 0x2FAB82E4AEF1D8664874E1F194951856D48463C3E6BF9A8C68E234A629A6F50,
                "chain_id": 0x534E5F474F45524C49,
                "nonce": 0x0,
                "tip": 0x0,
                "paymaster_data": [],
                "nonce_data_availability_mode": DAMode.L1,
                "fee_data_availability_mode": DAMode.L1,
                "tx_prefix": TransactionHashPrefix.DEPLOY_ACCOUNT,
                "version": 0x3,
            },
            {
                "constructor_calldata": [
                    0x5CD65F3D7DAEA6C63939D659B8473EA0C5CD81576035A4D34E52FB06840196C
                ],
                "contract_address_salt": 0x0,
                "class_hash": 0x2338634F11772EA342365ABD5BE9D9DC8A6F44F159AD782FDEBD3DB5D969738,
            },
            0x29FD7881F14380842414CDFDD8D6C0B1F2174F8916EDCFEB1EDE1EB26AC3EF0,
        ),
    ),
)
def test_compute_deploy_account_v3_transaction_hash(
    common_data, deploy_account_data, expected_hash
):
    assert (
        compute_deploy_account_v3_transaction_hash(
            **deploy_account_data,
            common_fields=CommonTransactionV3Fields(
                **common_data,
                resource_bounds=MAX_RESOURCE_BOUNDS,
            ),
        )
        == expected_hash
    )
