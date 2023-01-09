from starkware.starknet.services.api.gateway.transaction import AccountTransaction as AT
from starkware.starknet.services.api.gateway.transaction import ContractClass as CD
from starkware.starknet.services.api.gateway.transaction import Declare as DCL
from starkware.starknet.services.api.gateway.transaction import DeployAccount as DAC
from starkware.starknet.services.api.gateway.transaction import InvokeFunction as IF
from starkware.starknet.services.api.gateway.transaction import Transaction as T

from starknet_py.utils.docs import as_our_module

Invoke = InvokeFunction = as_our_module(IF)
StarknetTransaction = as_our_module(T)
AccountTransaction = as_our_module(AT)
ContractClass = as_our_module(CD)
Declare = as_our_module(DCL)
DeployAccount = as_our_module(DAC)
