from marshmallow import fields, post_load

from starknet_py.net.client_models import StateDiff
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.contracts_nonce import ContractsNonceSchema
from starknet_py.net.schemas.rpc.declared_contract_hash import (
    DeclaredContractHashSchema,
)
from starknet_py.net.schemas.rpc.deployed_contract_schema import DeployedContractSchema
from starknet_py.net.schemas.rpc.replaced_class_schema import ReplacedClassSchema
from starknet_py.net.schemas.rpc.storage_diff import StorageDiffSchema
from starknet_py.utils.schema import Schema


class StateDiffSchema(Schema):
    storage_diffs = fields.List(
        fields.Nested(StorageDiffSchema()),
        data_key="storage_diffs",
        required=True,
    )
    deprecated_declared_classes = fields.List(
        Felt(),
        data_key="deprecated_declared_classes",
        required=True,
    )
    declared_classes = fields.List(
        fields.Nested(DeclaredContractHashSchema()),
        data_key="declared_classes",
        required=True,
    )
    deployed_contracts = fields.List(
        fields.Nested(DeployedContractSchema()),
        data_key="deployed_contracts",
        required=True,
    )
    replaced_classes = fields.List(
        fields.Nested(ReplacedClassSchema()),
        data_key="replaced_classes",
        required=True,
    )
    nonces = fields.List(
        fields.Nested(ContractsNonceSchema()), data_key="nonces", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StateDiff:
        return StateDiff(**data)
