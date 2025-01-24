from starknet_py.constants import OutsideExecutionInterfaceID
from starknet_py.net.client_models import OutsideExecution
from starknet_py.net.schemas.common import Revision
from starknet_py.utils.typed_data import TypedData

OUTSIDE_EXECUTION_INTERFACE_ID_TO_TYPED_DATA_REVISION = {
    OutsideExecutionInterfaceID.V1: Revision.V0,
    OutsideExecutionInterfaceID.V2: Revision.V1,
}


# TODO(#1537): Implement as method of OutsideExecution
def outside_execution_to_typed_data(
    outside_execution: OutsideExecution,
    outside_execution_version: OutsideExecutionInterfaceID,
    chain_id: int,
) -> TypedData:
    """
    SNIP-12 Typed Data for OutsideExecution implementation. For revision V0 and V1.
    """

    revision = OUTSIDE_EXECUTION_INTERFACE_ID_TO_TYPED_DATA_REVISION[
        outside_execution_version
    ]

    if revision == Revision.V0:
        return TypedData.from_dict(
            {
                "types": {
                    "StarkNetDomain": [
                        {"name": "name", "type": "felt"},
                        {"name": "version", "type": "felt"},
                        {"name": "chainId", "type": "felt"},
                    ],
                    "OutsideExecution": [
                        {"name": "caller", "type": "felt"},
                        {"name": "nonce", "type": "felt"},
                        {"name": "execute_after", "type": "felt"},
                        {"name": "execute_before", "type": "felt"},
                        {"name": "calls_len", "type": "felt"},
                        {"name": "calls", "type": "OutsideCall*"},
                    ],
                    "OutsideCall": [
                        {"name": "to", "type": "felt"},
                        {"name": "selector", "type": "felt"},
                        {"name": "calldata_len", "type": "felt"},
                        {"name": "calldata", "type": "felt*"},
                    ],
                },
                "primaryType": "OutsideExecution",
                "domain": {
                    "name": "Account.execute_from_outside",
                    "version": "1",
                    "chainId": str(chain_id),
                    "revision": Revision.V0,
                },
                "message": {
                    "caller": outside_execution.caller,
                    "nonce": outside_execution.nonce,
                    "execute_after": outside_execution.execute_after,
                    "execute_before": outside_execution.execute_before,
                    "calls_len": len(outside_execution.calls),
                    "calls": [
                        {
                            "to": call.to_addr,
                            "selector": call.selector,
                            "calldata_len": len(call.calldata),
                            "calldata": call.calldata,
                        }
                        for call in outside_execution.calls
                    ],
                },
            }
        )

    # revision == Revision.V1
    return TypedData.from_dict(
        {
            "types": {
                "StarknetDomain": [
                    {"name": "name", "type": "shortstring"},
                    {"name": "version", "type": "shortstring"},
                    {"name": "chainId", "type": "shortstring"},
                    {"name": "revision", "type": "shortstring"},
                ],
                "OutsideExecution": [
                    {"name": "Caller", "type": "ContractAddress"},
                    {"name": "Nonce", "type": "felt"},
                    {"name": "Execute After", "type": "u128"},
                    {"name": "Execute Before", "type": "u128"},
                    {"name": "Calls", "type": "Call*"},
                ],
                "Call": [
                    {"name": "To", "type": "ContractAddress"},
                    {"name": "Selector", "type": "selector"},
                    {"name": "Calldata", "type": "felt*"},
                ],
            },
            "primaryType": "OutsideExecution",
            "domain": {
                "name": "Account.execute_from_outside",
                "version": "2",
                "chainId": str(chain_id),
                "revision": Revision.V1,
            },
            "message": {
                "Caller": outside_execution.caller,
                "Nonce": outside_execution.nonce,
                "Execute After": outside_execution.execute_after,
                "Execute Before": outside_execution.execute_before,
                "Calls": [
                    {
                        "To": call.to_addr,
                        "Selector": call.selector,
                        "Calldata": call.calldata,
                    }
                    for call in outside_execution.calls
                ],
            },
        }
    )
