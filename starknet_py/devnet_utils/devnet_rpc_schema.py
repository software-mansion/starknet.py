from marshmallow import fields, post_load

from starknet_py.devnet_utils.devnet_client_models import (
    Balance,
    BalanceRecord,
    Config,
    ForkConfig,
    IncreaseTimeResponse,
    MessageToL1,
    MessageToL2,
    MintResponse,
    PostmanFlushResponse,
    PredeployedAccount,
    ServerConfig,
    SetTimeResponse,
)
from starknet_py.net.schemas.common import Felt, PriceUnitField
from starknet_py.utils.schema import Schema

# pylint: disable=unused-argument, no-self-use


class MintResponseSchema(Schema):
    new_balance = fields.Integer(data_key="new_balance", required=True)
    unit = PriceUnitField(data_key="unit", required=True)
    tx_hash = Felt(data_key="tx_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> MintResponse:
        return MintResponse(**data)


class BalanceRecordSchema(Schema):
    amount = fields.Integer(data_key="amount", required=True)
    unit = PriceUnitField(data_key="unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BalanceRecord:
        return BalanceRecord(**data)


class BalanceSchema(Schema):
    eth = fields.Nested(BalanceRecordSchema(), data_key="eth", required=True)
    strk = fields.Nested(BalanceRecordSchema(), data_key="strk", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Balance:
        return Balance(**data)


class MessageToL1Schema(Schema):
    from_address = Felt(data_key="from_address", required=True)
    to_address = Felt(data_key="to_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> MessageToL1:
        return MessageToL1(**data)


class MessageToL2Schema(Schema):
    l2_contract_address = Felt(data_key="l2_contract_address", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)
    l1_contract_address = Felt(data_key="l1_contract_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)
    paid_fee_on_l1 = Felt(data_key="paid_fee_on_l1", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> MessageToL2:
        return MessageToL2(**data)


class PostmanFlushResponseSchema(Schema):
    messages_to_l1 = fields.List(
        fields.Nested(MessageToL1Schema(), data_key="messages_to_l1", required=False)
    )
    messages_to_l2 = fields.List(
        fields.Nested(MessageToL2Schema(), data_key="messages_to_l2", required=False)
    )
    generated_l2_transactions = fields.List(
        Felt(), data_key="generated_l2_transactions", required=False
    )
    l1_provider = fields.String(data_key="l1_provider", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> PostmanFlushResponse:
        return PostmanFlushResponse(**data)


class PredeployedAccountSchema(Schema):
    initial_balance = fields.Integer(data_key="initial_balance", required=True)
    address = Felt(data_key="address", required=True)
    public_key = Felt(data_key="public_key", required=True)
    private_key = Felt(data_key="private_key", required=True)
    balance = fields.Nested(
        BalanceSchema(), data_key="balance", load_default=None, required=False
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> PredeployedAccount:
        return PredeployedAccount(**data)


class ForkConfigSchema(Schema):
    url = fields.String(data_key="url", required=False, load_default=None)
    block_number = fields.Integer(
        data_key="block_number", required=False, load_default=None
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ForkConfig:
        return ForkConfig(**data)


class ServerConfigSchema(Schema):
    host = fields.String(data_key="host", required=True)
    port = fields.Integer(data_key="port", required=True)
    timeout = fields.Integer(data_key="timeout", required=True)
    request_body_size_limit = fields.Integer(
        data_key="request_body_size_limit", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ServerConfig:
        return ServerConfig(**data)


class ConfigSchema(Schema):
    seed = fields.Integer(data_key="seed", required=True)
    total_accounts = fields.Integer(data_key="total_accounts", required=True)
    account_contract_class = fields.String(
        data_key="account_contract_class", required=False
    )
    account_contract_class_hash = Felt(
        data_key="account_contract_class_hash", required=False
    )
    predeployed_accounts_initial_balance = fields.String(
        data_key="predeployed_accounts_initial_balance", required=True
    )
    start_time = fields.Integer(
        data_key="start_time", required=False, load_default=None
    )
    gas_price_wei = fields.Integer(data_key="gas_price_wei", required=True)
    gas_price_strk = fields.Integer(data_key="gas_price_strk", required=True)
    data_gas_price_wei = fields.Integer(data_key="data_gas_price_wei", required=True)
    data_gas_price_strk = fields.Integer(data_key="data_gas_price_strk", required=True)
    chain_id = fields.String(data_key="chain_id", required=True)
    dump_on = fields.Integer(data_key="dump_on", required=False, load_default=None)
    dump_path = fields.String(data_key="dump_path", required=False, load_default=None)
    block_generation_on = fields.String(data_key="block_generation_on", required=True)
    lite_mode = fields.Boolean(data_key="lite_mode", required=True)
    state_archive = fields.String(data_key="state_archive", required=True)
    fork_config = fields.Nested(
        ForkConfigSchema(), data_key="fork_config", required=True
    )
    disable_account_impersonation = fields.Boolean(
        data_key="disable_account_impersonation", required=True
    )
    server_config = fields.Nested(
        ServerConfigSchema(), data_key="server_config", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> Config:
        return Config(**data)


class IncreasedTimeResponseSchema(Schema):
    timestamp_increased_by = fields.Integer(
        data_key="timestamp_increased_by", required=True
    )
    block_hash = Felt(data_key="block_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> IncreaseTimeResponse:
        return IncreaseTimeResponse(**data)


class SetTimeResponseSchema(Schema):
    block_timestamp = fields.Integer(data_key="block_timestamp", required=True)
    block_hash = Felt(data_key="block_hash", required=False, load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SetTimeResponse:
        return SetTimeResponse(**data)
