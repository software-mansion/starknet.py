import datetime

from starknet_py.hash.outside_execution import outside_execution_to_typed_data
from starknet_py.net.client_models import OutsideExecution, Call
from starknet_py.net.models import StarknetChainId

from starknet_py.constants import SNIP9InterfaceVersion


def test_generate_message_hash_for_execute_outside_transaction():
    now = datetime.datetime(2024, 4, 12, 0, 0, 0)
    execute_after = now - datetime.timedelta(days=1)
    execute_before = now - datetime.timedelta(days=1)

    execution = OutsideExecution(
        caller=0x00000000000000000000000000000000011234567,
        nonce=0x00000000000000000000000000000000011234567,
        execute_after=int(execute_after.timestamp()),
        execute_before=int(execute_before.timestamp()),
        calls=[
            Call(
                to_addr=0x00000000012736721676273672,
                selector=0x72832873827382738273827,
                calldata=[]
            )
        ]
    )

    message_hash = outside_execution_to_typed_data(
        execution,
        SNIP9InterfaceVersion.V1,
        StarknetChainId.SEPOLIA
    ).message_hash(0x00000000001)

    assert message_hash == 0x54dbfd11fa2b470d9ae26560c0284aeba6545c2368c7f6d92c4c4052eb1acbc
