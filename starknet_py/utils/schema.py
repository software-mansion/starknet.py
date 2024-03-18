import os

from marshmallow import EXCLUDE, RAISE
from marshmallow import Schema as MarshmallowSchema


class Schema(MarshmallowSchema):
    class Meta:
        unknown = EXCLUDE if os.environ.get("STARKNET_PY_MARSHMALLOW_UKNOWN_EXCLUDE") else RAISE
