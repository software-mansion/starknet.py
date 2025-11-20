import pytest

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.constants import STRK_FEE_CONTRACT_ADDRESS
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call, TransactionExecutionStatus
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.eth_signer import EthSigner
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


# pylint: disable=line-too-long
# First 2 key pairs are retrieved from the mnemonic "test test test test test test test test test test test junk"
@pytest.mark.parametrize(
    "private_key, expected_public_key",
    [
        (
            "0xAC0974BEC39A17E36BA4A6B4D238FF944BACB478CBED5EFCAE784D7BF4F2FF80",
            0x8318535B54105D4A7AAE60C08FC45F9687181B4FDFC625BD1A753FA7397FED753547F11CA8696646F2F3ACB08E31016AFAC23E630C5D11F59F61FEF57B0D2AA5,
        ),
        (
            0x59C6995E998F97A5A0044966F0945389DC9E86DAE88C7A8412F4603B6B78690D,
            0xBA5734D8F7091719471E7F7ED6B9DF170DC70CC661CA05E688601AD984F068B0D67351E5F06073092499336AB0839EF8A521AFD334E53807205FA2F08EEC74F4,
        ),
        (
            0x525BC68475C0955FAE83869BEEC0996114D4BB27B28B781ED2A20EF23121B8DE,
            0x0178BB97615B49070EEFAD71CB2F159392274404E41DB748D9397147CB25CF597EBFCF2F399E635B72B99B8F76E9080763C65A42C842869815039D912150DDFE,
        ),
    ],
)
def test_pub_key(private_key, expected_public_key):
    eth_signer = EthSigner(
        private_key,
        chain_id=StarknetChainId.MAINNET,
    )
    assert eth_signer.public_key == expected_public_key


@pytest.mark.parametrize(
    "loaded_typed_data, expected_r, expected_s, expected_v",
    [
        (
            "typed_data_rev_0_example.json",
            (0xFF887F391242BB244E9E10D5DA01CB8A, 0x665E69338D4E0772039D4A032B01B07B),
            (0xF84A88E94CABBA842AB4ACCF8ADC0200, 0x61C82A3A2F1A9340620E634BEBECB20B),
            0x1,
        ),
        (
            "typed_data_rev_0_struct_array_example.json",
            (0x936821B8F85EEE978AAF9127814742D2, 0x31BC82F3C096425CFCCBBC08CD06130),
            (0x57E8E66F612B1C612DBFD159BDB8B260, 0x4341F2213DFF450FFF4EA979EA5A48A0),
            0x0,
        ),
        (
            "typed_data_rev_1_example.json",
            (0x47EED1FC641A07E66D699D1F3B1D94E8, 0x9C93AA4098668FECF0CD5E7B37D82A92),
            (0xEE8CC16FF762F7AF5B221AAA75177CC6, 0x4F6CFAB88C2AB909E4B80EBCEE151671),
            0x0,
        ),
    ],
    indirect=["loaded_typed_data"],
)
def test_message_hash(loaded_typed_data, expected_r, expected_s, expected_v):
    eth_signer = EthSigner(
        private_key=0x525BC68475C0955FAE83869BEEC0996114D4BB27B28B781ED2A20EF23121B8DE,
        chain_id=StarknetChainId.MAINNET,
    )
    signed_message = eth_signer.sign_message(
        loaded_typed_data,
        0x65A822FBEE1AE79E898688B5A4282DC79E0042CBED12F6169937FDDB4C26641,
    )

    assert len(signed_message) == 5
    assert signed_message[0] == expected_r[0]
    assert signed_message[1] == expected_r[1]
    assert signed_message[2] == expected_s[0]
    assert signed_message[3] == expected_s[1]
    assert signed_message[4] == expected_v


@pytest.mark.asyncio
async def test_sign_transaction(eth_account, map_contract):
    map_call = Call(
        to_addr=map_contract.address,
        selector=get_selector_from_name("put"),
        calldata=[100, 101],
    )

    signed_tx = await eth_account.sign_invoke_v3(
        calls=map_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    calldata = (
        [signed_tx.calculate_hash(StarknetChainId.SEPOLIA)]
        + [len(signed_tx.signature)]
        + signed_tx.signature
    )

    validate_call = Call(
        to_addr=eth_account.address,
        selector=get_selector_from_name("is_valid_signature"),
        calldata=calldata,
    )
    (res,) = await eth_account.client.call_contract(call=validate_call)
    assert res == encode_shortstring("VALID")


@pytest.mark.asyncio
async def test_send_transaction(eth_account):
    call = Call(
        to_addr=int(STRK_FEE_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("transfer"),
        calldata=[0x12345, 10000, 0],
    )
    res = await eth_account.execute_v3(calls=call, resource_bounds=MAX_RESOURCE_BOUNDS)

    receipt = await eth_account.client.get_transaction_receipt(res.transaction_hash)

    assert receipt.execution_status == TransactionExecutionStatus.SUCCEEDED
