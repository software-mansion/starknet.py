from dataclasses import dataclass
from typing import List, Optional

from starknet_py.net.client_models import Hash, PriceUnit


@dataclass
class MintResponse:
    """
    Represents the result of a mint operation, including the new balance.
    """

    new_balance: int
    unit: PriceUnit
    tx_hash: Hash


@dataclass
class BalanceRecord:
    amount: int
    unit: PriceUnit


@dataclass
class Balance:
    eth: BalanceRecord
    strk: BalanceRecord


@dataclass
class PostmanFlushResponse:
    messages_to_l1: List[Hash]
    messages_to_l2: List[Hash]
    generated_l2_transactions: List[Hash]
    l1_provider: str


@dataclass
class PredeployedAccount:
    initial_balance: int
    address: Hash
    public_key: Hash
    private_key: Hash
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
    account_contract_class_hash: Optional[Hash]
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
    block_hash: Hash


@dataclass
class SetTimeResponse:
    block_timestamp: int
    block_hash: Optional[Hash] = None
