from marshmallow import Schema, fields, post_load
from starknet_py.net.base_client import BlockHashIdentifier, BlockNumberIdentifier


class BlockHashIdentifierSchema(Schema):
    block_hash = fields.Integer()
    index = fields.Integer()


class BlockNumberIdentifierSchema(Schema):
    block_number = fields.Integer()
    index = fields.Integer()
