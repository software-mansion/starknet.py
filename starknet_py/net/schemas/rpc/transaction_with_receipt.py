from marshmallow import fields, post_load

from starknet_py.net.client_models import TransactionWithReceipt
from starknet_py.net.schemas.rpc.transaction_receipt import TransactionReceiptSchema
from starknet_py.net.schemas.rpc.types_of_transactions import TypesOfTransactionsSchema
from starknet_py.utils.schema import Schema


class TransactionWithReceiptSchema(Schema):
    transaction = fields.Nested(TypesOfTransactionsSchema(), data_key="transaction")
    receipt = fields.Nested(TransactionReceiptSchema(), data_key="receipt")

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionWithReceipt:
        return TransactionWithReceipt(**data)
