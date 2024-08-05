from dataclasses import dataclass
from typing import List, Optional

from starknet_py.net.client_models import PriceUnit


@dataclass
class MintResponse:
    """
    Represents the result of a mint operation, including the new balance.
    """

    new_balance: int
    unit: PriceUnit
    tx_hash: int


@dataclass
class BalanceRecord:
    amount: int
    unit: PriceUnit


@dataclass
class Balance:
    eth: BalanceRecord
    strk: BalanceRecord


@dataclass
class MessageToL1:
    from_address: int
    to_address: int
    payload: List[int]


@dataclass
class MessageToL2:
    l2_contract_address: int
    entry_point_selector: int
    l1_contract_address: int
    payload: List[int]
    paid_fee_on_l1: int
    nonce: int


@dataclass
class PostmanFlushResponse:
    messages_to_l1: List[MessageToL1]
    messages_to_l2: List[MessageToL2]
    generated_l2_transactions: List[int]
    l1_provider: str


@dataclass
class PredeployedAccount:
    initial_balance: int
    address: int
    public_key: int
    private_key: int
    balance: Optional[Balance] = None


@dataclass
class ForkConfig:
    url: Optional[str]
    block_number: Optional[int]


@dataclass
class ServerConfig:
    host: str
    port: int
    timeout: int
    request_body_size_limit: int


# pylint: disable=too-many-instance-attributes
@dataclass
class Config:
    seed: int
    total_accounts: int
    account_contract_class_hash: Optional[int]
    predeployed_accounts_initial_balance: str
    gas_price_wei: int
    gas_price_strk: int
    data_gas_price_wei: int
    data_gas_price_strk: int
    chain_id: str
    block_generation_on: str
    lite_mode: bool
    fork_config: ForkConfig
    disable_account_impersonation: bool
    server_config: ServerConfig
    account_contract_class: Optional[str] = None
    state_archive: Optional[str] = None
    start_time: Optional[int] = None
    dump_on: Optional[int] = None
    dump_path: Optional[str] = None


@dataclass
class IncreaseTimeResponse:
    timestamp_increased_by: int
    block_hash: int


@dataclass
class SetTimeResponse:
    block_timestamp: int
    block_hash: Optional[int] = None
