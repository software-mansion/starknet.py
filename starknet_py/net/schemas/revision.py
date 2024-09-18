from marshmallow import  ValidationError, fields
from typing import Any , Optional
from starknet_py.net.schemas.common import Enum

class Revision(Enum):
    """
    Enum representing the revision of the specification to be used.
    """

    V0 = 0
    V1 = 1


class RevisionField(fields.Field):
    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs):
        if value is None or value == Revision.V0:
            return str(Revision.V0.value)
        return value.value

    def _deserialize(self, value, attr, data, **kwargs) -> Revision:
        if isinstance(value, str):
            value = int(value)

        revisions = [revision.value for revision in Revision]
        if value not in revisions:
            allowed_revisions_str = "".join(list(map(str, revisions)))
            raise ValidationError(
                f"Invalid value provided for Revision: {value}. Allowed values are {allowed_revisions_str}."
            )

        return Revision(value)
