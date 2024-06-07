from marshmallow import fields, post_load

from starknet_py.net.client_models import ExecutionResources
from starknet_py.net.schemas.rpc.computation_resources import ComputationResourcesSchema
from starknet_py.net.schemas.rpc.data_resources import DataResourcesSchema


class ExecutionResourcesSchema(ComputationResourcesSchema):
    data_availability = fields.Nested(
        DataResourcesSchema(), data_key="data_availability", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ExecutionResources:
        return ExecutionResources(**data)
