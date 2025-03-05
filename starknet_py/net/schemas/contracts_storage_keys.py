from marshmallow import fields

from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class ContractsStorageKeysSchema(Schema):
    contract_address = Felt(data_key="contract_address", required=True)
    storage_keys = fields.List(Felt(), data_key="storage_keys", required=True)
