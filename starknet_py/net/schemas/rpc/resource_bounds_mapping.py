from marshmallow import fields, post_load

from starknet_py.net.client_models import ResourceBoundsMapping
from starknet_py.net.schemas.rpc.resource_bounds import ResourceBoundsSchema
from starknet_py.utils.schema import Schema


class ResourceBoundsMappingSchema(Schema):
    l1_gas = fields.Nested(ResourceBoundsSchema(), data_key="l1_gas", required=True)
    l2_gas = fields.Nested(ResourceBoundsSchema(), data_key="l2_gas", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ResourceBoundsMapping:
        return ResourceBoundsMapping(**data)
