from marshmallow import fields
from marshmallow_oneofschema.one_of_schema import OneOfSchema

from starknet_py.net.client_models import TransactionType
from starknet_py.net.schemas.rpc.contract import SierraCompiledContractSchema
from starknet_py.net.schemas.rpc.transactions import (
    DeclareTransactionV3Schema,
    DeployAccountTransactionV3Schema,
    InvokeTransactionV3Schema,
)


class BroadcastedDeclareV3Schema(DeclareTransactionV3Schema):
    contract_class = fields.Nested(
        SierraCompiledContractSchema(), data_key="contract_class", required=True
    )


class BroadcastedTransactionSchema(OneOfSchema):
    type_schemas = {
        TransactionType.INVOKE.name: InvokeTransactionV3Schema(),
        TransactionType.DECLARE.name: BroadcastedDeclareV3Schema(),
        TransactionType.DEPLOY_ACCOUNT.name: DeployAccountTransactionV3Schema(),
    }

    def get_obj_type(self, obj):
        return obj.type.name
