from marshmallow import fields, post_load

from starknet_py.net.client_models import StorageDiffItem
from starknet_py.net.schemas.common import Felt, StorageEntrySchema
from starknet_py.utils.schema import Schema


class StorageDiffSchema(Schema):
    address = Felt(data_key="address", required=True)
    storage_entries = fields.List(
        fields.Nested(StorageEntrySchema()),
        data_key="storage_entries",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StorageDiffItem:
        return StorageDiffItem(**data)
