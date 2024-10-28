from typing import Any, Optional

from marshmallow import ValidationError, fields, post_load

from starknet_py.net.client_models import NodeHashToNodeMappingItem
from starknet_py.net.schemas.common import Felt, NumberAsHex
from starknet_py.utils.schema import Schema


class BinaryNodeSchema(Schema):
    left = fields.Integer(required=True)
    right = fields.Integer(required=True)


class EdgeNodeSchema(Schema):
    path = NumberAsHex(required=True)
    length = fields.Integer(required=True)
    child = Felt(required=True)


class MerkleNodeSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.binary_node_keys = set(BinaryNodeSchema().fields.keys())
        self.edge_node_keys = set(EdgeNodeSchema().fields.keys())

    @post_load
    def make_dataclass(self, data, **kwargs):
        # pylint: disable=no-self-use
        data_keys = set(data.keys())

        if data_keys == self.binary_node_keys:
            return BinaryNodeSchema().load(data, **kwargs)
        elif data_keys == self.edge_node_keys:
            return EdgeNodeSchema().load(data, **kwargs)
        else:
            raise ValidationError(f"Invalid data provided for MerkleNode: {data}.")


class NodeHashToNodeMappingField(fields.Field):
    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs):
        if value is None:
            return None
        return [NodeHashToNodeMappingItemSchema().dump(obj=item) for item in value]

    def _deserialize(self, value: Any, attr: Optional[str], data: Any, **kwargs):
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValidationError("Expected a list.")
        return [NodeHashToNodeMappingItemSchema().load(data=obj) for obj in value]


class NodeHashToNodeMappingItemSchema(Schema):
    node_hash = Felt(data_key="node_hash", required=True)
    node = fields.Nested(MerkleNodeSchema(), required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        # pylint: disable=no-self-use
        return NodeHashToNodeMappingItem(**data)


class ContractLeafDataSchema(Schema):
    nonce = Felt(required=True)
    class_hash = Felt(required=True)


class GlobalRootsSchema(Schema):
    contracts_tree_root = fields.Integer(required=True)
    classes_tree_root = fields.Integer(required=True)
    block_hash = fields.Integer(required=True)


class ContractsProofSchema(Schema):
    nodes = NodeHashToNodeMappingField(required=True)
    contract_leaves_data = fields.List(
        fields.Nested(ContractLeafDataSchema()), required=True
    )


class StorageProofResponseSchema(Schema):
    classes_proof = fields.List(
        fields.Nested(NodeHashToNodeMappingItemSchema()), required=True
    )
    contracts_proof = fields.Nested(ContractsProofSchema(), required=True)
    contracts_storage_proofs = fields.List(NodeHashToNodeMappingField(), required=True)
    global_roots = fields.Nested(GlobalRootsSchema(), required=True)
