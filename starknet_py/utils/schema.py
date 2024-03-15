import os

from marshmallow import EXCLUDE, RAISE
from marshmallow import Schema as SchemaToCopy

print(os.environ.get("marshmallow_raise"))


class Schema(SchemaToCopy):
    class Meta:
        unknown = RAISE if os.environ.get("marshmallow_raise") else EXCLUDE
