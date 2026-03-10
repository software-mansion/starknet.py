import asyncio

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.contract import Contract
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call, ResourceBoundsMapping

# from starknet_py.net.client_models import Call, TransactionResponseFlag
from starknet_py.net.client_utils import _to_rpc_felt
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair


async def main():
    client = FullNodeClient("http://188.34.188.184:7171/rpc/v0_10")
    # res = await client.get_chain_id()
    account_address = 0x42A18CD953DFD974E3901160FBE4681023B66C6736457CEF9B6670A034F37CF
    account = Account(
        address=account_address,
        key_pair=KeyPair.from_private_key(
            0x6D5B039736FE67BD2691199AF052B4C810FFB4B6613FBCDD803E403DF54C9B2
        ),
        client=client,
        chain=StarknetChainId.SEPOLIA_INTEGRATION,
    )
    contract_address = (
        0x047382CAF000C78CB056485D5CB5FA373162A9A195B39C270775CFBC3213136E
    )

    call = Call(
        to_addr=contract_address,
        # to_addr=0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d,
        selector=get_selector_from_name("get_balance"),
        # selector=get_selector_from_name("balance_of"),
        calldata=[],
        # calldata=[account_address],
    )
    # invoke = await account.sign_invoke_v3(calls=[call], auto_estimate=True)
    print("-----")
    result = await account.execute_v3(
        call,
        # auto_estimate=True,
        resource_bounds=ResourceBoundsMapping.init_with_zeros(),
        # proof=[11],
        # proof_facts=[88314448135728, 26704351219188916681607892819, 10],
    )

    print(result)
    print("-----")

    receipt = await client.wait_for_tx(result.transaction_hash)

    tx_with_proof = await client.get_transaction(
        tx_hash=receipt.transaction_hash,
        # response_flags=[TransactionResponseFlag.INCLUDE_PROOF_FACTS],
    )
    tx_without_proof = await client.get_transaction(tx_hash=receipt.transaction_hash)
    print(tx_with_proof)
    print(tx_without_proof)


if __name__ == "__main__":
    asyncio.run(main())
