from marshmallow import fields, validate

from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema

STORAGE_KEY_PATTERN = r"^0x(0|[0-7]{1}[a-fA-F0-9]{0,62})$"


class StorageKeySchema(fields.Str):
    """
    Storage key schema, represented as a string of hex digits
    """

    def __init__(self, **kwargs):
        super().__init__(
            validate=validate.Regexp(
                regex=STORAGE_KEY_PATTERN,
                error=f"Storage key must match the pattern: {STORAGE_KEY_PATTERN}",
            ),
            **kwargs,
        )


class ContractsStorageKeysSchema(Schema):
    contract_address = Felt(data_key="contract_address", required=True)
    storage_keys = fields.List(
        StorageKeySchema(), data_key="storage_keys", required=True
    )
