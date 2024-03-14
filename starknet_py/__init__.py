from marshmallow import EXCLUDE, RAISE, Schema

Schema.Meta.unknown = EXCLUDE  # type: ignore
