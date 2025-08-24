from marshmallow import fields, post_load
from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.paymaster.models import (
    AccountDeploymentData,
    DefaultFeeMode,
    DeployAndInvokeBuildTransactionResponse,
    DeployBuildTransactionResponse,
    ExecuteTransactionResponse,
    FeeEstimate,
    FeeMode,
    InvokeBuildTransactionResponse,
    PriorityFeeMode,
    SponsoredFeeMode,
    TokenData,
    TrackingIdResponse,
    TrackingStatus,
    UserParameters,
    UserTransaction,
)
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema
from starknet_py.utils.typed_data import TypedDataSchema


class AccountDeploymentDataSchema(Schema):
    address = Felt(data_key="address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)
    salt = Felt(data_key="salt", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    sigdata = fields.List(Felt(), data_key="sigdata", required=False)
    version = fields.Integer(data_key="version", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> AccountDeploymentData:
        return AccountDeploymentData(**data)


class CallSchema(Schema):
    to = Felt(data_key="to", required=True)
    selector = Felt(data_key="selector", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)


class UserInvokeSchema(Schema):
    user_address = Felt(data_key="user_address", required=True)
    calls = fields.List(fields.Nested(CallSchema), data_key="calls", required=True)


class InvokeTransactionSchema(Schema):
    invoke = fields.Nested(UserInvokeSchema, data_key="invoke", required=True)


class DeployTransactionSchema(Schema):
    deployment = fields.Nested(
        AccountDeploymentDataSchema, data_key="deployment", required=True
    )


class DeployAndInvokeTransactionSchema(Schema):
    invoke = fields.Nested(UserInvokeSchema, data_key="invoke", required=True)
    deployment = fields.Nested(
        AccountDeploymentDataSchema, data_key="deployment", required=True
    )


class UserTransactionSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "invoke": InvokeTransactionSchema(),
        "deploy": DeployTransactionSchema(),
        "deploy_and_invoke": DeployAndInvokeTransactionSchema(),
    }

    def get_obj_type(self, obj: UserTransaction):
        return obj.type


class TokenDataSchema(Schema):
    token_address = Felt(data_key="token_address", required=True)
    decimals = fields.Integer(data_key="decimals", required=True)
    price_in_strk = Felt(data_key="price_in_strk", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> TokenData:
        return TokenData(**data)


class TrackingStatusField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs) -> TrackingStatus:
        return TrackingStatus(value)


class TrackingIdResponseSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    status = TrackingStatusField(data_key="status", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> TrackingIdResponse:
        return TrackingIdResponse(**data)


class FeeEstimateSchema(Schema):
    gas_token_price_in_strk = Felt(data_key="gas_token_price_in_strk", required=True)
    estimated_fee_in_strk = Felt(data_key="estimated_fee_in_strk", required=True)
    estimated_fee_in_gas_token = Felt(
        data_key="estimated_fee_in_gas_token", required=True
    )
    suggested_max_fee_in_strk = Felt(
        data_key="suggested_max_fee_in_strk", required=True
    )
    suggested_max_fee_in_gas_token = Felt(
        data_key="suggested_max_fee_in_gas_token", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> FeeEstimate:
        return FeeEstimate(**data)


class TimeBoundsSchema(Schema):
    execute_after = fields.DateTime(
        data_key="execute_after", format="timestamp_ms", required=True
    )
    execute_before = fields.Integer(
        data_key="execute_before", format="timestamp_ms", required=True
    )


class SponsoredFeeModeSchema(Schema):
    pass


class DefaultFeeModeSchema(Schema):
    gas_token = Felt(data_key="gas_token", required=True)


class PriorityFeeModeSchema(Schema):
    gas_token = Felt(data_key="gas_token", required=True)
    tip_in_strk = Felt(data_key="tip_in_strk", required=True)


class FeeModeSchema(OneOfSchema):
    type_field = "mode"
    type_schemas = {
        "sponsored": SponsoredFeeModeSchema(),
        "default": DefaultFeeModeSchema(),
        "priority": PriorityFeeModeSchema(),
    }

    def get_obj_type(self, obj: FeeMode):
        if isinstance(obj, SponsoredFeeMode):
            return "sponsored"
        if isinstance(obj, DefaultFeeMode):
            return "default"
        if isinstance(obj, PriorityFeeMode):
            return "priority"
        raise Exception(f"Unknown FeeMode type: {type(obj)}")


class UserParametersSchema(Schema):
    version = fields.String(data_key="version", required=True)
    fee_mode = fields.Nested(FeeModeSchema, data_key="fee_mode", required=False)
    time_bounds = fields.Nested(
        TimeBoundsSchema, data_key="time_bounds", required=False
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> UserParameters:
        return UserParameters(**data)


class ExecuteTransactionResponseSchema(Schema):
    tracking_id = Felt(data_key="tracking_id", required=True)
    transaction_hash = Felt(data_key="transaction_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ExecuteTransactionResponse:
        return ExecuteTransactionResponse(**data)


class DeployBuildTransactionResponseSchema(Schema):
    deployment = fields.Nested(
        AccountDeploymentDataSchema, data_key="deployment", required=True
    )
    parameters = fields.Nested(
        UserParametersSchema, data_key="parameters", required=True
    )
    fee = fields.Nested(FeeEstimateSchema, data_key="fee", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployBuildTransactionResponse:
        return DeployBuildTransactionResponse(**data)


class InvokeBuildTransactionResponseSchema(Schema):
    typed_data = fields.Nested(TypedDataSchema, data_key="typed_data", required=True)
    parameters = fields.Nested(
        UserParametersSchema, data_key="parameters", required=True
    )
    fee = fields.Nested(FeeEstimateSchema, data_key="fee", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> InvokeBuildTransactionResponse:
        return InvokeBuildTransactionResponse(**data)


class DeployAndInvokeBuildTransactionResponseSchema(Schema):
    deployment = fields.Nested(
        AccountDeploymentDataSchema, data_key="deployment", required=True
    )
    typed_data = fields.Dict(data_key="typed_data", required=True)
    parameters = fields.Nested(
        UserParametersSchema, data_key="parameters", required=True
    )
    fee = fields.Nested(FeeEstimateSchema, data_key="fee", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAndInvokeBuildTransactionResponse:
        return DeployAndInvokeBuildTransactionResponse(**data)


class BuildTransactionResponseSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "deploy": DeployBuildTransactionResponseSchema(),
        "invoke": InvokeBuildTransactionResponseSchema(),
        "deploy_and_invoke": DeployAndInvokeBuildTransactionResponseSchema(),
    }


class ExecutableUserInvokeSchema(Schema):
    user_address = Felt(data_key="user_address", required=True)
    typed_data = fields.Nested(TypedDataSchema, data_key="typed_data", required=True)
    signature = fields.List(Felt(), data_key="signature", required=True)


class ExecutableInvokeTransactionSchema(Schema):
    invoke = fields.Nested(ExecutableUserInvokeSchema, data_key="invoke", required=True)


class ExecutableDeployTransactionSchema(Schema):
    deployment = fields.Nested(
        AccountDeploymentDataSchema, data_key="deployment", required=True
    )


class ExecutableDeployAndInvokeTransactionSchema(Schema):
    deployment = fields.Nested(
        AccountDeploymentDataSchema, data_key="deployment", required=True
    )
    invoke = fields.Nested(ExecutableUserInvokeSchema, data_key="invoke", required=True)


class ExecutableUserTransactionSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "invoke": ExecutableInvokeTransactionSchema(),
        "deploy": ExecutableDeployTransactionSchema(),
        "deploy_and_invoke": ExecutableDeployAndInvokeTransactionSchema(),
    }

    def get_obj_type(self, obj: UserTransaction):
        return obj.type
