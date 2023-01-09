from dataclasses import dataclass


@dataclass
class EstimatedFee:
    overall_fee: int
    gas_price: int
    gas_usage: int
