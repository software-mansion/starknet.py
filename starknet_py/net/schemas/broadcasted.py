
from starknet_py.net.schemas.rpc import DeclareTransactionV1Schema, DeclareTransactionV2Schema, DeclareTransactionV3Schema, DeployAccountTransactionV1Schema, DeployAccountTransactionV3Schema, InvokeTransactionV1Schema, InvokeTransactionV3Schema

from starknet_py.net.schemas.common import TransactionTypeField

from starknet_py.net.schemas.gateway import ContractClassSchema, SierraCompiledContractSchema
from marshmallow import EXCLUDE, fields
from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.schemas.utils import _extract_tx_version

class DeclareBroadcastedV3Schema(DeclareTransactionV3Schema):
    type = TransactionTypeField(data_key='type')
    contract_class = fields.Nested(
        SierraCompiledContractSchema(), data_key="contract_class"
    )

class DeclareBroadcastedV2Schema(DeclareTransactionV2Schema):
    type = TransactionTypeField(data_key='type')
    contract_class = fields.Nested(
        SierraCompiledContractSchema(), data_key="contract_class"
    )


class DeclareBroadcastedV1Schema(DeclareTransactionV1Schema):
    type = TransactionTypeField(data_key='type')
    contract_class = fields.Nested(ContractClassSchema(), data_key = 'contract_class')

  
class DeclareBroadcastedSchema(OneOfSchema):
    type_schemas = {
        1: DeclareBroadcastedV1Schema,
        2: DeclareBroadcastedV2Schema,
        3: DeclareBroadcastedV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)
    
class InvokeBroadcastedSchema(OneOfSchema):
    type_schemas = {
        1: InvokeTransactionV1Schema,
        3: InvokeTransactionV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)
    
class DeployAccountBroadcastedSchema(OneOfSchema):
    type_schemas = {
        1: DeployAccountTransactionV1Schema,
        3: DeployAccountTransactionV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)
    
class TransactionTraceSchema(OneOfSchema):
    type_schemas = {
        "INVOKE": InvokeBroadcastedSchema(),
        "DECLARE": DeclareBroadcastedSchema(),
        "DEPLOY_ACCOUNT": DeployAccountBroadcastedSchema(),
    }

    def get_obj_type(self, obj):
        return obj.type.name
