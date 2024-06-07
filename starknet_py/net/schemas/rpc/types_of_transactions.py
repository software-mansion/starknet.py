from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.schemas.rpc.declare_transaction import DeclareTransactionSchema
from starknet_py.net.schemas.rpc.deploy_account_transaction import (
    DeployAccountTransactionSchema,
)
from starknet_py.net.schemas.rpc.deploy_transaction import DeployTransactionSchema
from starknet_py.net.schemas.rpc.invoke_transaction import InvokeTransactionSchema
from starknet_py.net.schemas.rpc.l1_handler_transaction import (
    L1HandlerTransactionSchema,
)


class TypesOfTransactionsSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "INVOKE": InvokeTransactionSchema,
        "DECLARE": DeclareTransactionSchema,
        "DEPLOY": DeployTransactionSchema,
        "DEPLOY_ACCOUNT": DeployAccountTransactionSchema,
        "L1_HANDLER": L1HandlerTransactionSchema,
    }
