from marshmallow import fields, post_load

from starknet_py.net.client_models import RevertedFunctionInvocation
from starknet_py.utils.schema import Schema


class RevertedFunctionInvocationSchema(Schema):
    revert_reason = fields.String(data_key="revert_reason", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> RevertedFunctionInvocation:
        return RevertedFunctionInvocation(**data)
