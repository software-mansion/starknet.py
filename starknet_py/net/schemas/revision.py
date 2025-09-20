from typing import Any, Optional

from marshmallow import ValidationError, fields

from starknet_py.net.models.typed_data import Revision


class RevisionField(fields.Field):
    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs):
        if value is None or value == Revision.V0:
            return str(Revision.V0.value)
        return value.value

    def _deserialize(self, value, attr, data, **kwargs) -> Revision:
        if isinstance(value, str):
            value = int(value)

        if isinstance(value, Revision):
            value = value.value

        revisions = [revision.value for revision in Revision]
        if value not in revisions:
            allowed_revisions_str = "".join(list(map(str, revisions)))
            raise ValidationError(
                f"Invalid value provided for Revision: {value}. Allowed values are {allowed_revisions_str}."
            )

        return Revision(value)
