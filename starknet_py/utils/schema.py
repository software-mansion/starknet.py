import os

from marshmallow import EXCLUDE, RAISE
from marshmallow import Schema as MarshmallowSchema
from marshmallow import SchemaOpts

MARSHMALLOW_UNKNOWN_EXCLUDE = os.environ.get("STARKNET_PY_MARSHMALLOW_UNKNOWN_EXCLUDE")


class UnknownOpts(SchemaOpts):

    def __init__(self, meta, **kwargs):
        SchemaOpts.__init__(self, meta, **kwargs)
        self.unknown = (
            EXCLUDE if (MARSHMALLOW_UNKNOWN_EXCLUDE or "").lower() == "true" else RAISE
        )


# TODO(#1564): `ExcludeOpts` should be removed once issue is resolved.
class ExcludeOpts(SchemaOpts):

    def __init__(self, meta, **kwargs):
        SchemaOpts.__init__(self, meta, **kwargs)
        self.unknown = EXCLUDE


class Schema(MarshmallowSchema):
    OPTIONS_CLASS = UnknownOpts
