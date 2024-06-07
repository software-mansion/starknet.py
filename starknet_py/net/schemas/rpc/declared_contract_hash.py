from marshmallow import post_load

from starknet_py.net.client_models import DeclaredContractHash
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class DeclaredContractHashSchema(Schema):
    class_hash = Felt(data_key="class_hash", required=True)
    compiled_class_hash = Felt(data_key="compiled_class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclaredContractHash:
        return DeclaredContractHash(**data)
