from typing import List, Union

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.utils.typed_data.types import TypedData


def get_hex(value: Union[int, str]):
    if isinstance(value, str):
        if value[:2] == "0x":
            return value
        return hex(encode_shortstring(value))
    return hex(value)


def get_dependencies(typed_data: TypedData, type_: str) -> List[str]:
    if type_ and type_[-1] == "*":
        type_ = type_[:-1]

    if type_ not in typed_data.types:
        return []
    dependencies = set()

    def get_deps(type_: str):
        for item in typed_data.types[type_]:
            item_type = item["type"]
            if item_type in typed_data.types and item_type not in dependencies:
                dependencies.add(item_type)
                get_deps(item_type)

    get_deps(type_)
    return [type_, *list(dependencies)]


def encode_type(typed_data: TypedData, type_: str) -> str:
    [primary, *dependencies] = get_dependencies(typed_data, type_)
    types = [primary, *sorted(dependencies)]

    def make_dependency_str(dependency):
        lst = [f"{t['name']}:{t['type']}" for t in typed_data.types[dependency]]
        return f"{dependency}({','.join(lst)})"

    return "".join([make_dependency_str(x) for x in types])


def get_type_hash(typed_data: TypedData, type_: str) -> int:
    return get_selector_from_name(encode_type(typed_data, type_))


def encode_value(typed_data: TypedData, type_: str, value: Union[int, str]) -> str:
    if type_ in typed_data.types:
        return [type_, get_struct_hash(typed_data, type_, value)]
    return [type_, int(get_hex(value), 16)]


def encode_data(typed_data: TypedData, type_: str, data: dict) -> List[List[str]]:
    def encode(field):
        if data[field["name"]] is None:
            raise ValueError(f"Cannot encode data: missing data for {field['name']}")
        value = data[field["name"]]
        return encode_value(typed_data, field["type"], value)

    types = ["felt"]
    values = [get_type_hash(typed_data, type_)]

    for item in typed_data.types[type_]:
        typ, val = encode(item)
        types.append(typ)
        values.append(val)

    return [types, values]


def get_struct_hash(typed_data: TypedData, type_: str, data: dict) -> int:
    encoded_data = encode_data(typed_data, type_, data)
    return compute_hash_on_elements(encoded_data[1])


def get_message_hash(typed_data: TypedData, account_address: int) -> int:
    message = [
        encode_shortstring("StarkNet Message"),
        get_struct_hash(typed_data, "StarkNetDomain", typed_data.domain),
        account_address,
        get_struct_hash(typed_data, typed_data.primary_type, typed_data.message),
    ]

    return compute_hash_on_elements(message)
