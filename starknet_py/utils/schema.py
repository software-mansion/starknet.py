import os

from marshmallow import EXCLUDE, RAISE
from marshmallow import Schema as MarshmallowSchema

MARSHMALLOW_UNKNOWN_EXCLUDE = os.environ.get("STARKNET_PY_MARSHMALLOW_UNKNOWN_EXCLUDE")


class Schema(MarshmallowSchema):
    class Meta:
        unknown = (
            EXCLUDE if (MARSHMALLOW_UNKNOWN_EXCLUDE or "").lower() == "true" else RAISE
        )
