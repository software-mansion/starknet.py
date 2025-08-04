import pytest

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.constants import STRK_FEE_CONTRACT_ADDRESS
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call, TransactionExecutionStatus
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.eth_signer import EthSigner
from starknet_py.serialization import Uint256Serializer
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.utils import _new_address, prepay_account


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
async def test_validate_signature(
    client, eth_account_class_hash, eth_fee_contract, strk_fee_contract
):
    signer = EthSigner(
        0x525BC68475C0955FAE83869BEEC0996114D4BB27B28B781ED2A20EF23121B8DE,
        chain_id=StarknetChainId.SEPOLIA,
    )

    # Manually serialize u512 into felt array
    serializer = Uint256Serializer()
    public_key_bytes = signer.public_key.to_bytes(64, byteorder="big")
    constructor_calldata = serializer.serialize(
        int.from_bytes(public_key_bytes[:32], byteorder="big")
    ) + serializer.serialize(int.from_bytes(public_key_bytes[32:], byteorder="big"))

    address, salt = _new_address(eth_account_class_hash, constructor_calldata)

    await prepay_account(
        address=address,
        eth_fee_contract=eth_fee_contract,
        strk_fee_contract=strk_fee_contract,
    )

    account = Account(
        address=address,
        client=client,
        signer=signer,
        chain=StarknetChainId.SEPOLIA.value,
    )

    deploy_account_tx = await account.sign_deploy_account_v3(
        class_hash=eth_account_class_hash,
        contract_address_salt=salt,
        constructor_calldata=constructor_calldata,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    await client.deploy_account(deploy_account_tx)

    # Signature calculated first using starknet.js
    # This is a call to the Map contract with
    # address: 0x77AF8BE78F9AB70BA5DB594A079D53FB692256ACCA4F65ED4681BE63F766F8
    # selector: put
    # calldata: [100, 101]
    call = Call(
        to_addr=address,
        selector=get_selector_from_name("is_valid_signature"),
        calldata=[
            0x78EDDEAD1D83CF611C1C78B488BC3CBFEFF0696E9464EA967676100BBC1E674,  # tx hash
            0x5,
            0x89B5C415C2F37F5A6D1292EDC15958B2,
            0xA2EC923770F021309C58B7FA68A6A4CE,
            0xC4AE697F7D4999C9C6F6C6F13C97EF65,
            0x1792B1FB77858EE84EF3244807A73A16,
            0x0,
        ],
    )
    (res,) = await client.call_contract(call=call)
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
