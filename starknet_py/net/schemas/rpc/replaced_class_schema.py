from marshmallow import post_load

from starknet_py.net.client_models import ReplacedClass
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class ReplacedClassSchema(Schema):
    contract_address = Felt(data_key="contract_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ReplacedClass:
        return ReplacedClass(**data)
