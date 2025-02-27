from marshmallow import fields
from marshmallow_oneofschema.one_of_schema import OneOfSchema

from starknet_py.net.client_models import TransactionType
from starknet_py.net.schemas.rpc.contract import SierraCompiledContractSchema
from starknet_py.net.schemas.rpc.transactions import (
    DeclareTransactionV3Schema,
    DeployAccountTransactionSchema,
    InvokeTransactionSchema,
)
from starknet_py.net.schemas.utils import _extract_tx_version


class BroadcastedDeclareV3Schema(DeclareTransactionV3Schema):
    contract_class = fields.Nested(
        SierraCompiledContractSchema(), data_key="contract_class", required=True
    )


class BroadcastedDeclareSchema(OneOfSchema):
    type_schemas = {
        "3": BroadcastedDeclareV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)


class BroadcastedTransactionSchema(OneOfSchema):
    type_schemas = {
        TransactionType.INVOKE.name: InvokeTransactionSchema(),
        TransactionType.DECLARE.name: BroadcastedDeclareSchema(),
        TransactionType.DEPLOY_ACCOUNT.name: DeployAccountTransactionSchema(),
    }

    def get_obj_type(self, obj):
        return obj.type.name
