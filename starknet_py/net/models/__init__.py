from starkware.starknet.services.api.gateway.transaction import (
    InvokeFunction as IF,
    Deploy as D,
    Transaction as T,
)

from starknet_py.utils.docs import as_our_module
from .address import *

InvokeFunction = as_our_module(IF)
Deploy = as_our_module(D)
Transaction = as_our_module(T)
