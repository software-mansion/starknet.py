from collections import OrderedDict
from typing import Dict, Iterable, List, Tuple

from starknet_py.net.client_models import Call, Calls
from starknet_py.net.models import Invoke
from starknet_py.serialization import PayloadSerializer
from starknet_py.serialization.data_serializers.array_serializer import ArraySerializer
from starknet_py.serialization.data_serializers.felt_serializer import FeltSerializer
from starknet_py.serialization.data_serializers.struct_serializer import (
    StructSerializer,
)
from starknet_py.utils.iterable import ensure_iterable


async def prepare_invoke(
    calls: Calls,
    max_fee: int = 0,
    nonce: int = 0,
    version: int = 1,
    contract_address: int = 0,
) -> Invoke:
    """
    Takes calls and creates Invoke from them.

    :param calls: Single call or list of calls.
    :param max_fee: Max amount of Wei to be paid when executing transaction.
    :param nonce: Nonce of the transaction.
    :param version: Version of the transaction.
    :param contract_address: Address of the contract.
    :return: Invoke created from the calls (without the signature).
    """
    call_descriptions, calldata = _merge_calls(ensure_iterable(calls))
    wrapped_calldata = _execute_payload_serializer.serialize(
        {"call_array": call_descriptions, "calldata": calldata}
    )

    invoke = Invoke(
        calldata=wrapped_calldata,
        signature=[],
        max_fee=max_fee,
        version=version,
        nonce=nonce,
        contract_address=contract_address,
    )
    return invoke


def _merge_calls(calls: Iterable[Call]) -> Tuple[List[Dict], List[int]]:
    call_descriptions = []
    entire_calldata = []
    for call in calls:
        data, entire_calldata = _parse_call(call, entire_calldata)
        call_descriptions.append(data)

    return call_descriptions, entire_calldata


def _parse_call(call: Call, entire_calldata: List) -> Tuple[Dict, List]:
    _data = {
        "to": call.to_addr,
        "selector": call.selector,
        "data_offset": len(entire_calldata),
        "data_len": len(call.calldata),
    }
    entire_calldata += call.calldata

    return _data, entire_calldata


_felt_serializer = FeltSerializer()
_call_description = StructSerializer(
    OrderedDict(
        to=_felt_serializer,
        selector=_felt_serializer,
        data_offset=_felt_serializer,
        data_len=_felt_serializer,
    )
)
_execute_payload_serializer = PayloadSerializer(
    OrderedDict(
        call_array=ArraySerializer(_call_description),
        calldata=ArraySerializer(_felt_serializer),
    )
)
