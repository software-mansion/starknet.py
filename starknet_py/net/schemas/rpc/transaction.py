from marshmallow import fields

from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class TransactionSchema(Schema):
    hash = Felt(data_key="transaction_hash", load_default=None)
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    version = Felt(data_key="version", required=True)
