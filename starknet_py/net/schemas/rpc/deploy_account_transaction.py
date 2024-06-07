from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.schemas.rpc.deploy_account_transaction_v1 import (
    DeployAccountTransactionV1Schema,
)
from starknet_py.net.schemas.rpc.deploy_account_transaction_v3 import (
    DeployAccountTransactionV3Schema,
)
from starknet_py.net.schemas.utils import _extract_tx_version


class DeployAccountTransactionSchema(OneOfSchema):
    type_schemas = {
        1: DeployAccountTransactionV1Schema,
        3: DeployAccountTransactionV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)

    def get_data_type(self, data):
        return _extract_tx_version(data.get("version"))
