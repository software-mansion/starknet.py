from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.schemas.rpc.declare_transaction_trace import (
    DeclareTransactionTraceSchema,
)
from starknet_py.net.schemas.rpc.deploy_account_transaction_trace import (
    DeployAccountTransactionTraceSchema,
)
from starknet_py.net.schemas.rpc.invoke_transaction_trace import (
    InvokeTransactionTraceSchema,
)
from starknet_py.net.schemas.rpc.l1_handler_transaction_trace import (
    L1HandlerTransactionTraceSchema,
)


class TransactionTraceSchema(OneOfSchema):
    type_field = "type"

    type_schemas = {
        "INVOKE": InvokeTransactionTraceSchema(),
        "DECLARE": DeclareTransactionTraceSchema(),
        "DEPLOY_ACCOUNT": DeployAccountTransactionTraceSchema(),
        "L1_HANDLER": L1HandlerTransactionTraceSchema(),
    }
