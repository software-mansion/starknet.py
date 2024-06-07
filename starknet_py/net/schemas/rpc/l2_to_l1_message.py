from marshmallow import fields, post_load

from starknet_py.net.client_models import L2toL1Message
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class L2toL1MessageSchema(Schema):
    l2_address = Felt(data_key="from_address", required=True)
    l1_address = Felt(data_key="to_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L2toL1Message:
        return L2toL1Message(**data)
