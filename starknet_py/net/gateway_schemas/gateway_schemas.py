from marshmallow import Schema, fields, post_load

from starknet_py.net.client_models import Transaction


class TransactionSchema(Schema):
    hash = fields.Integer(data_key="transaction_hash")
    contract_address = fields.Integer(data_key="contract_address")
    entry_point_selector = fields.Integer(data_key="entry_point_selector")
    calldata = fields.List(fields.Integer(), data_key="calldata")

    @post_load
    def make_transaction(self, data, **kwargs) -> Transaction:
        # TODO handle kwargs
        return Transaction(**data)
