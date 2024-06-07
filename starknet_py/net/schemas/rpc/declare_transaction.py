from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.schemas.rpc.declare_transaction_v0 import (
    DeclareTransactionV0Schema,
)
from starknet_py.net.schemas.rpc.declare_transaction_v1 import (
    DeclareTransactionV1Schema,
)
from starknet_py.net.schemas.rpc.declare_transaction_v2 import (
    DeclareTransactionV2Schema,
)
from starknet_py.net.schemas.rpc.declare_transaction_v3 import (
    DeclareTransactionV3Schema,
)
from starknet_py.net.schemas.utils import _extract_tx_version


class DeclareTransactionSchema(OneOfSchema):
    type_schemas = {
        0: DeclareTransactionV0Schema,
        1: DeclareTransactionV1Schema,
        2: DeclareTransactionV2Schema,
        3: DeclareTransactionV3Schema,
    }

    def get_data_type(self, data):
        return _extract_tx_version(data.get("version"))
