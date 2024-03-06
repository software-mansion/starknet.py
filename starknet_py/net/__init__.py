import os

from marshmallow import EXCLUDE, INCLUDE, Schema

# Setting strategy taken from
# https://github.com/marshmallow-code/marshmallow/issues/1367

if strategy := os.getenv(key="RESPONSE_UNKNOWN_FIELDS_STRATEGY"):
    if strategy == "EXCLUDE":
        Schema.Meta.unknown = EXCLUDE  # type: ignore
    elif strategy == "INCLUDE":
        Schema.Meta.unknown = INCLUDE  # type: ignore
