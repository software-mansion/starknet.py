from marshmallow import fields

from starknet_py.net.schemas.common import Felt, L1DAModeField
from starknet_py.net.schemas.rpc.resource_price import ResourcePriceSchema
from starknet_py.utils.schema import Schema


class PendingBlockHeaderSchema(Schema):
    parent_hash = Felt(data_key="parent_hash", required=True)
    timestamp = fields.Integer(data_key="timestamp", required=True)
    sequencer_address = Felt(data_key="sequencer_address", required=True)
    l1_gas_price = fields.Nested(
        ResourcePriceSchema(), data_key="l1_gas_price", required=True
    )
    l1_data_gas_price = fields.Nested(
        ResourcePriceSchema(), data_key="l1_data_gas_price", required=True
    )
    l1_da_mode = L1DAModeField(data_key="l1_da_mode", required=True)
    starknet_version = fields.String(data_key="starknet_version", required=True)
