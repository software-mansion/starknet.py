from marshmallow import fields, post_load

from starknet_py.net.client_models import DataResources
from starknet_py.utils.schema import Schema


class DataResourcesSchema(Schema):
    l1_gas = fields.Integer(data_key="l1_gas", required=True)
    l1_data_gas = fields.Integer(data_key="l1_data_gas", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DataResources:
        return DataResources(**data)
