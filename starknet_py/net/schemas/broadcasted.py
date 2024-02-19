from marshmallow import fields, post_dump
from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.models.transaction import compress_program
from starknet_py.net.schemas.common import TransactionTypeField
from starknet_py.net.schemas.gateway import (
    ContractClassSchema,
    SierraCompiledContractSchema,
)
from starknet_py.net.schemas.rpc import (
    DeclareTransactionV1Schema,
    DeclareTransactionV2Schema,
    DeclareTransactionV3Schema,
    DeployAccountTransactionSchema,
    InvokeTransactionSchema,
)
from starknet_py.net.schemas.utils import _extract_tx_version


class DeclareBroadcastedV3Schema(DeclareTransactionV3Schema):
    contract_class = fields.Nested(
        SierraCompiledContractSchema(), data_key="contract_class"
    )


class DeclareBroadcastedV2Schema(DeclareTransactionV2Schema):
    contract_class = fields.Nested(
        SierraCompiledContractSchema(), data_key="contract_class"
    )


class DeclareBroadcastedV1Schema(DeclareTransactionV1Schema):
    contract_class = fields.Nested(ContractClassSchema(), data_key="contract_class")

    @post_dump
    def post_dump(self, data, **kwargs):
        # Allowing **kwargs is needed here because marshmallow is passing additional parameters here
        # along with data, which we don't handle.
        # pylint: disable=unused-argument, no-self-use
        return compress_program(data)


class DeclareBroadcastedSchema(OneOfSchema):
    type_schemas = {
        1: DeclareBroadcastedV1Schema,
        2: DeclareBroadcastedV2Schema,
        3: DeclareBroadcastedV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)


class TransactionTraceSchema(OneOfSchema):
    type_schemas = {
        "INVOKE": InvokeTransactionSchema(),
        "DECLARE": DeclareBroadcastedSchema(),
        "DEPLOY_ACCOUNT": DeployAccountTransactionSchema(),
    }

    def get_obj_type(self, obj):
        return obj.type.name
