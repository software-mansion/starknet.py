from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.schemas.rpc.function_invocation import FunctionInvocationSchema
from starknet_py.net.schemas.rpc.reverted_function_invocation import (
    RevertedFunctionInvocationSchema,
)


class ExecuteInvocationSchema(OneOfSchema):
    type_schemas = {
        "REVERTED": RevertedFunctionInvocationSchema(),
        "FUNCTION_INVOCATION": FunctionInvocationSchema(),
    }

    def get_data_type(self, data):
        if "revert_reason" in data:
            return "REVERTED"
        return "FUNCTION_INVOCATION"
