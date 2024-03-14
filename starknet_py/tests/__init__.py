from marshmallow import RAISE, Schema

Schema.Meta.unknown = RAISE  # type: ignore
