from typing import Any, Optional, Union

from marshmallow import ValidationError, fields, post_load

from starknet_py.net.client_models import (
    BinaryNode,
    ContractLeafData,
    ContractsProof,
    EdgeNode,
    GlobalRoots,
    NodeHashToNodeMappingItem,
    StorageProofResponse,
)
from starknet_py.net.schemas.common import Felt, NumberAsHex
from starknet_py.utils.schema import Schema


class BinaryNodeSchema(Schema):
    left = fields.Integer(data_key="left", required=True)
    right = fields.Integer(data_key="right", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BinaryNode:
        return BinaryNode(**data)


class EdgeNodeSchema(Schema):
    path = NumberAsHex(data_key="path", required=True)
    length = fields.Integer(data_key="length", required=True)
    child = Felt(data_key="child", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EdgeNode:
        return EdgeNode(**data)


class MerkleNodeSchema(Schema):
    @post_load
    def make_dataclass(self, data, **kwargs) -> Union[BinaryNode, EdgeNode]:
        # pylint: disable=no-self-use
        binary_node_keys = set(BinaryNodeSchema().fields.keys())
        edge_node_keys = set(EdgeNodeSchema().fields.keys())

        data_keys = set(data.keys())

        if data_keys == binary_node_keys:
            return BinaryNode(**data)
        elif data_keys == edge_node_keys:
            return EdgeNode(**data)
        raise ValidationError(f"Invalid data provided for MerkleNode: {data}.")


class NodeHashToNodeMappingField(fields.Field):
    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs):
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValidationError(
                f"Invalid value provided for NodeHashToNodeMapping: {value}. Expected a list."
            )
        return [NodeHashToNodeMappingItemSchema().dump(item) for item in value]

    def _deserialize(self, value: Any, attr: Optional[str], data: Any, **kwargs):
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValidationError(
                f"Invalid value provided for NodeHashToNodeMapping: {value}. Expected a list."
            )
        return [NodeHashToNodeMappingItemSchema().load(item) for item in value]


class NodeHashToNodeMappingItemSchema(Schema):
    node_hash = Felt(data_key="node_hash", required=True)
    node = fields.Nested(MerkleNodeSchema(), data_key="node", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> NodeHashToNodeMappingItem:
        return NodeHashToNodeMappingItem(**data)


class ContractLeafDataSchema(Schema):
    nonce = Felt(data_key="nonce", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractLeafData:
        return ContractLeafData(**data)


class GlobalRootsSchema(Schema):
    contracts_tree_root = fields.Integer(data_key="contracts_tree_root", required=True)
    classes_tree_root = fields.Integer(data_key="classes_tree_root", required=True)
    block_hash = fields.Integer(data_key="block_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> GlobalRoots:
        return GlobalRoots(**data)


class ContractsProofSchema(Schema):
    nodes = NodeHashToNodeMappingField(data_key="nodes", required=True)
    contract_leaves_data = fields.List(
        fields.Nested(ContractLeafDataSchema()),
        data_key="contract_leaves_data",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractsProof:
        return ContractsProof(**data)


class StorageProofResponseSchema(Schema):
    classes_proof = fields.List(
        fields.Nested(NodeHashToNodeMappingItemSchema()),
        data_key="classes_proof",
        required=True,
    )
    contracts_proof = fields.Nested(
        ContractsProofSchema(), data_key="contracts_proof", required=True
    )
    contracts_storage_proofs = fields.List(
        NodeHashToNodeMappingField(), data_key="contracts_storage_proofs", required=True
    )
    global_roots = fields.Nested(
        GlobalRootsSchema(), data_key="global_roots", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StorageProofResponse:
        return StorageProofResponse(**data)
