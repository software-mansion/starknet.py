from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.schemas.rpc.invoke_transaction_v0 import InvokeTransactionV0Schema
from starknet_py.net.schemas.rpc.invoke_transaction_v1 import InvokeTransactionV1Schema
from starknet_py.net.schemas.rpc.invoke_transaction_v3 import InvokeTransactionV3Schema
from starknet_py.net.schemas.utils import _extract_tx_version


class InvokeTransactionSchema(OneOfSchema):
    type_schemas = {
        0: InvokeTransactionV0Schema,
        1: InvokeTransactionV1Schema,
        3: InvokeTransactionV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)

    def get_data_type(self, data):
        return _extract_tx_version(data.get("version"))
