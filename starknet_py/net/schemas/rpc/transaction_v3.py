from marshmallow import fields

from starknet_py.net.client_models import DAMode
from starknet_py.net.schemas.common import DAModeField, Felt, Uint64
from starknet_py.net.schemas.rpc.resource_bounds_mapping import (
    ResourceBoundsMappingSchema,
)
from starknet_py.net.schemas.rpc.transaction import TransactionSchema


class TransactionV3Schema(TransactionSchema):
    tip = Uint64(data_key="tip", load_default=0)
    nonce_data_availability_mode = DAModeField(
        data_key="nonce_data_availability_mode", load_default=DAMode.L1
    )
    fee_data_availability_mode = DAModeField(
        data_key="fee_data_availability_mode", load_default=DAMode.L1
    )
    paymaster_data = fields.List(Felt(), data_key="paymaster_data", load_default=[])
    resource_bounds = fields.Nested(
        ResourceBoundsMappingSchema(), data_key="resource_bounds", required=True
    )
