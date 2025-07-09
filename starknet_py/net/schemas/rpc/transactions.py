from marshmallow import fields, post_load
from marshmallow_oneofschema.one_of_schema import OneOfSchema

from starknet_py.net.client_models import (
    DAMode,
    DeclareTransactionResponse,
    DeclareTransactionV0,
    DeclareTransactionV1,
    DeclareTransactionV2,
    DeclareTransactionV3,
    DeployAccountTransactionResponse,
    DeployAccountTransactionV1,
    DeployAccountTransactionV3,
    DeployTransaction,
    FeePayment,
    InvokeTransactionV0,
    InvokeTransactionV1,
    InvokeTransactionV3,
    L1HandlerTransaction,
    L2toL1Message,
    MessageStatus,
    ResourceBounds,
    ResourceBoundsMapping,
    SentTransactionResponse,
    TransactionReceipt,
    TransactionStatusResponse,
    TransactionWithReceipt,
)
from starknet_py.net.schemas.common import (
    DAModeField,
    ExecutionStatusField,
    Felt,
    FinalityStatusField,
    MessageFinalityStatusField,
    NumberAsHex,
    PriceUnitField,
    StatusField,
    TransactionTypeField,
    Uint64,
    Uint128,
)
from starknet_py.net.schemas.rpc.event import EventSchema
from starknet_py.net.schemas.rpc.general import ExecutionResourcesSchema
from starknet_py.net.schemas.utils import _extract_tx_version
from starknet_py.utils.schema import Schema


class L2toL1MessageSchema(Schema):
    l2_address = Felt(data_key="from_address", required=True)
    l1_address = Felt(data_key="to_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L2toL1Message:
        return L2toL1Message(**data)


class FeePaymentSchema(Schema):
    amount = Felt(data_key="amount", required=True)
    unit = PriceUnitField(data_key="unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> FeePayment:
        return FeePayment(**data)


class TransactionReceiptSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    execution_status = ExecutionStatusField(data_key="execution_status", required=True)
    finality_status = FinalityStatusField(data_key="finality_status", required=True)
    block_number = fields.Integer(data_key="block_number", load_default=None)
    block_hash = Felt(data_key="block_hash", load_default=None)
    actual_fee = fields.Nested(FeePaymentSchema(), data_key="actual_fee", required=True)
    type = TransactionTypeField(data_key="type", required=True)
    contract_address = Felt(data_key="contract_address", load_default=None)
    revert_reason = fields.String(data_key="revert_reason", load_default=None)
    events = fields.List(
        fields.Nested(EventSchema()), data_key="events", load_default=[]
    )
    messages_sent = fields.List(
        fields.Nested(L2toL1MessageSchema()), data_key="messages_sent", load_default=[]
    )
    message_hash = NumberAsHex(data_key="message_hash", load_default=None)
    execution_resources = fields.Nested(
        ExecutionResourcesSchema(), data_key="execution_resources", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionReceipt:
        return TransactionReceipt(**data)


class TransactionStatusResponseSchema(Schema):
    finality_status = StatusField(data_key="finality_status", required=True)
    execution_status = ExecutionStatusField(
        data_key="execution_status", load_default=None
    )
    failure_reason = fields.String(data_key="failure_reason", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionStatusResponse:
        return TransactionStatusResponse(**data)


class ResourceBoundsSchema(Schema):
    max_amount = Uint64(data_key="max_amount", required=True)
    max_price_per_unit = Uint128(data_key="max_price_per_unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ResourceBounds:
        return ResourceBounds(**data)


class ResourceBoundsMappingSchema(Schema):
    l1_gas = fields.Nested(ResourceBoundsSchema(), data_key="l1_gas", required=True)
    l2_gas = fields.Nested(ResourceBoundsSchema(), data_key="l2_gas", required=True)
    l1_data_gas = fields.Nested(
        ResourceBoundsSchema(), data_key="l1_data_gas", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ResourceBoundsMapping:
        return ResourceBoundsMapping(**data)


class TransactionSchema(Schema):
    hash = Felt(data_key="transaction_hash", load_default=None)
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    version = Felt(data_key="version", required=True)


class DeprecatedTransactionSchema(TransactionSchema):
    max_fee = Felt(data_key="max_fee", required=True)


class TransactionV3Schema(TransactionSchema):
    tip = Uint64(data_key="tip", required=True)
    nonce_data_availability_mode = DAModeField(
        data_key="nonce_data_availability_mode", load_default=DAMode.L1
    )
    fee_data_availability_mode = DAModeField(
        data_key="fee_data_availability_mode", load_default=DAMode.L1
    )
    paymaster_data = fields.List(Felt(), data_key="paymaster_data", load_default=[])
    resource_bounds = fields.Nested(
        ResourceBoundsMappingSchema(), data_key="resource_bounds", required=True
    )


class InvokeTransactionV0Schema(DeprecatedTransactionSchema):
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    contract_address = Felt(data_key="contract_address", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransactionV0:
        return InvokeTransactionV0(**data)


class InvokeTransactionV1Schema(DeprecatedTransactionSchema):
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    sender_address = Felt(data_key="sender_address", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransactionV1:
        return InvokeTransactionV1(**data)


class InvokeTransactionV3Schema(TransactionV3Schema):
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    sender_address = Felt(data_key="sender_address", required=True)
    nonce = Felt(data_key="nonce", required=True)
    account_deployment_data = fields.List(
        Felt(), data_key="account_deployment_data", required=True
    )

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransactionV3:
        return InvokeTransactionV3(**data)


class DeclareTransactionV0Schema(DeprecatedTransactionSchema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV0:
        return DeclareTransactionV0(**data)


class DeclareTransactionV1Schema(DeprecatedTransactionSchema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV1:
        return DeclareTransactionV1(**data)


class DeclareTransactionV2Schema(DeprecatedTransactionSchema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)
    compiled_class_hash = Felt(data_key="compiled_class_hash", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV2:
        return DeclareTransactionV2(**data)


class DeclareTransactionV3Schema(TransactionV3Schema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    compiled_class_hash = Felt(data_key="compiled_class_hash", required=True)
    nonce = Felt(data_key="nonce", required=True)
    account_deployment_data = fields.List(
        Felt(), data_key="account_deployment_data", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV3:
        return DeclareTransactionV3(**data)


class DeployTransactionSchema(TransactionSchema):
    contract_address_salt = Felt(data_key="contract_address_salt", required=True)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployTransaction:
        return DeployTransaction(**data)


class DeployAccountTransactionV1Schema(DeprecatedTransactionSchema):
    nonce = Felt(data_key="nonce", required=True)
    contract_address_salt = Felt(data_key="contract_address_salt", required=True)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransactionV1:
        return DeployAccountTransactionV1(**data)


class DeployAccountTransactionV3Schema(TransactionV3Schema):
    nonce = Felt(data_key="nonce", required=True)
    contract_address_salt = Felt(data_key="contract_address_salt", required=True)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransactionV3:
        return DeployAccountTransactionV3(**data)


class DeclareTransactionSchema(OneOfSchema):
    type_schemas = {
        "0": DeclareTransactionV0Schema,
        "1": DeclareTransactionV1Schema,
        "2": DeclareTransactionV2Schema,
        "3": DeclareTransactionV3Schema,
    }

    def get_data_type(self, data):
        return _extract_tx_version(data.get("version"))


class InvokeTransactionSchema(OneOfSchema):
    type_schemas = {
        "0": InvokeTransactionV0Schema,
        "1": InvokeTransactionV1Schema,
        "3": InvokeTransactionV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)

    def get_data_type(self, data):
        return _extract_tx_version(data.get("version"))


class DeployAccountTransactionSchema(OneOfSchema):
    type_schemas = {
        "1": DeployAccountTransactionV1Schema,
        "3": DeployAccountTransactionV3Schema,
    }

    def get_obj_type(self, obj):
        return _extract_tx_version(obj.version)

    def get_data_type(self, data):
        return _extract_tx_version(data.get("version"))


class L1HandlerTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)
    nonce = NumberAsHex(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1HandlerTransaction:
        return L1HandlerTransaction(**data)


class TypesOfTransactionsSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "INVOKE": InvokeTransactionSchema,
        "DECLARE": DeclareTransactionSchema,
        "DEPLOY": DeployTransactionSchema,
        "DEPLOY_ACCOUNT": DeployAccountTransactionSchema,
        "L1_HANDLER": L1HandlerTransactionSchema,
    }


class TransactionWithReceiptSchema(Schema):
    transaction = fields.Nested(TypesOfTransactionsSchema(), data_key="transaction")
    receipt = fields.Nested(TransactionReceiptSchema(), data_key="receipt")

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionWithReceipt:
        return TransactionWithReceipt(**data)


class SentTransactionSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SentTransactionResponse:
        return SentTransactionResponse(**data)


class DeclareTransactionResponseSchema(SentTransactionSchema):
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionResponse:
        return DeclareTransactionResponse(**data)


class DeployAccountTransactionResponseSchema(SentTransactionSchema):
    address = Felt(data_key="contract_address", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransactionResponse:
        return DeployAccountTransactionResponse(**data)


class MessageStatusSchema(Schema):
    transaction_hash = NumberAsHex(data_key="transaction_hash", required=True)
    finality_status = MessageFinalityStatusField(
        data_key="finality_status", required=True
    )
    execution_status = ExecutionStatusField(data_key="execution_status", required=True)
    failure_reason = fields.String(data_key="failure_reason", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> MessageStatus:
        return MessageStatus(**data)
