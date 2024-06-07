from marshmallow import fields, post_load

from starknet_py.net.client_models import ComputationResources
from starknet_py.utils.schema import Schema


class ComputationResourcesSchema(Schema):
    steps = fields.Integer(data_key="steps", required=True)
    memory_holes = fields.Integer(data_key="memory_holes", load_default=None)
    range_check_builtin_applications = fields.Integer(
        data_key="range_check_builtin_applications", load_default=None
    )
    pedersen_builtin_applications = fields.Integer(
        data_key="pedersen_builtin_applications", load_default=None
    )
    poseidon_builtin_applications = fields.Integer(
        data_key="poseidon_builtin_applications", load_default=None
    )
    ec_op_builtin_applications = fields.Integer(
        data_key="ec_op_builtin_applications", load_default=None
    )
    ecdsa_builtin_applications = fields.Integer(
        data_key="ecdsa_builtin_applications", load_default=None
    )
    bitwise_builtin_applications = fields.Integer(
        data_key="bitwise_builtin_applications", load_default=None
    )
    keccak_builtin_applications = fields.Integer(
        data_key="keccak_builtin_applications", load_default=None
    )
    segment_arena_builtin = fields.Integer(
        data_key="segment_arena_builtin", load_default=None
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ComputationResources:
        return ComputationResources(**data)
