<div align="center">
    <img src="https://raw.githubusercontent.com/software-mansion/starknet.py/master/graphic.png" alt="starknet.py"/>
</div>
<h2 align="center">Starknet SDK for Python</h2>

<div align="center">

[![codecov](https://codecov.io/gh/software-mansion/starknet.py/branch/master/graph/badge.svg?token=3E54E8RYSL)](https://codecov.io/gh/software-mansion/starknet.py)
[![pypi](https://img.shields.io/pypi/v/starknet.py)](https://pypi.org/project/starknet.py/)
[![build](https://img.shields.io/github/actions/workflow/status/software-mansion/starknet.py/checks.yml)](https://github.com/software-mansion/starknet.py/actions)
[![docs](https://readthedocs.org/projects/starknetpy/badge/?version=latest)](https://starknetpy.readthedocs.io/en/latest/?badge=latest)
[![license](https://img.shields.io/badge/license-MIT-black)](https://github.com/software-mansion/starknet.py/blob/master/LICENSE.txt)
[![stars](https://img.shields.io/github/stars/software-mansion/starknet.py?color=yellow)](https://github.com/software-mansion/starknet.py/stargazers)
[![starkware](https://img.shields.io/badge/powered_by-StarkWare-navy)](https://starkware.co)

</div>

## 📘 Documentation

- [Installation](https://starknetpy.rtfd.io/en/latest/installation.html)
- [Quickstart](https://starknetpy.rtfd.io/en/latest/quickstart.html)
- [Guide](https://starknetpy.rtfd.io/en/latest/guide.html)
- [API](https://starknetpy.rtfd.io/en/latest/api.html)
- [Migration guide](https://starknetpy.readthedocs.io/en/latest/migration_guide.html)

## ⚙️ Installation

Installation varies between operating systems.

[See our documentation on complete instructions](https://starknetpy.rtfd.io/en/latest/installation.html)


## 💨 Quickstart
### Using FullNodeClient
A [Client](https://starknetpy.readthedocs.io/en/latest/api/client.html#client) is a facade for interacting with Starknet. 
[FullNodeClient](https://starknetpy.readthedocs.io/en/latest/api/full_node_client.html#module-starknet_py.net.full_node_client) is a client which interacts with a Starknet full nodes like [Pathfinder](https://github.com/eqlabs/pathfinder), [Papyrus](https://github.com/starkware-libs/papyrus) or [Juno](https://github.com/NethermindEth/juno). 
It supports read and write operations, like querying the blockchain state or adding new transactions.


```python
from starknet_py.net.full_node_client import FullNodeClient

node_url = "https://your.node.url"
client = FullNodeClient(node_url=node_url)

call_result = await client.get_block(block_number=1)
```
The default interface is asynchronous. Although it is the recommended way of using starknet.py, you can also use a synchronous version. It might be helpful to play with Starknet directly in python interpreter.

```python
node_url = "https://your.node.url"
client = FullNodeClient(node_url=node_url)
call_result = client.get_block_sync(block_number=1)
```
You can check out all of the FullNodeClient’s methods here: [FullNodeClient](https://starknetpy.readthedocs.io/en/latest/api/full_node_client.html#module-starknet_py.net.full_node_client).

### Creating Account
[Account](https://starknetpy.readthedocs.io/en/latest/api/account.html#starknet_py.net.account.account.Account) is the default implementation of [BaseAccount](https://starknetpy.readthedocs.io/en/latest/api/account.html#starknet_py.net.account.base_account.BaseAccount) interface. 
It supports an account contract which proxies the calls to other contracts on Starknet.

Account can be created in two ways:
- By constructor (It is required to provide an `address` and either `key_pair` or `signer`).
- By static method `Account.deploy_account_v3`

Additionally, you can use the [sncast](https://foundry-rs.github.io/starknet-foundry/starknet/index.html) tool to create an account, 
which will automatically be saved to a file.
There are some examples how to do it:
```python
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

# Creates an instance of account which is already deployed
# Account using transaction version=1 (has __validate__ function)
client = FullNodeClient(node_url="https://your.node.url")
account = Account(
    client=client,
    address="0x4321",
    key_pair=KeyPair(private_key=654, public_key=321),
    chain=StarknetChainId.SEPOLIA,
)

# There is another way of creating key_pair
key_pair = KeyPair.from_private_key(key=123)
# or
key_pair = KeyPair.from_private_key(key="0x123")

# Instead of providing key_pair it is possible to specify a signer
signer = StarkCurveSigner("0x1234", key_pair, StarknetChainId.SEPOLIA)

account = Account(
    client=client, address="0x1234", signer=signer, chain=StarknetChainId.SEPOLIA
)
```

### Using Account
Example usage:

```python
from starknet_py.contract import Contract
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
resource_bounds = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
)
# Declare and deploy an example contract which implements a simple k-v store.
# Contract.declare_v3 takes string containing a compiled contract (sierra) and
# a class hash (casm_class_hash) or string containing a compiled contract (casm)
declare_result = await Contract.declare_v3(
    account,
    compiled_contract=compiled_contract,
    compiled_class_hash=class_hash,
    resource_bounds=resource_bounds,
)

await declare_result.wait_for_acceptance()
deploy_result = await declare_result.deploy_v3(
    resource_bounds=resource_bounds,
)
# Wait until deployment transaction is accepted
await deploy_result.wait_for_acceptance()

# Get deployed contract
map_contract = deploy_result.deployed_contract
k, v = 13, 4324
# Adds a transaction to mutate the state of k-v store. The call goes through account proxy, because we've used
# Account to create the contract object
await (
    await map_contract.functions["put"].invoke_v3(
        k,
        v,
        resource_bounds=resource_bounds,
    )
).wait_for_acceptance()

# Retrieves the value, which is equal to 4324 in this case
(resp,) = await map_contract.functions["get"].call(k)

# There is a possibility of invoking the multicall

# Creates a list of prepared function calls
calls = [
    map_contract.functions["put"].prepare_invoke_v3(key=10, value=20),
    map_contract.functions["put"].prepare_invoke_v3(key=30, value=40),
]

# Executes only one transaction with prepared calls
transaction_response = await account.execute_v3(
    calls=calls,
    resource_bounds=resource_bounds,
)
await account.client.wait_for_tx(transaction_response.transaction_hash)
```

### Using Contract
[Contract](https://starknetpy.readthedocs.io/en/latest/api/contract.html#starknet_py.contract.Contract) makes interacting with contracts deployed on Starknet much easier:
```python
from starknet_py.contract import Contract
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping

contract_address = (
    "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"
)
key = 1234

# Create contract from contract's address - Contract will download contract's ABI to know its interface.
contract = await Contract.from_address(address=contract_address, provider=account)

# If the ABI is known, create the contract directly (this is the preferred way).
contract = Contract(
    address=contract_address,
    abi=abi,
    provider=account,
    cairo_version=1,
)

# All exposed functions are available at contract.functions.
# Here we invoke a function, creating a new transaction.
resource_bounds = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
)
invocation = await contract.functions["put"].invoke_v3(
        key,
        7,
        resource_bounds=resource_bounds,
)
# Invocation returns InvokeResult object. It exposes a helper for waiting until transaction is accepted.
await invocation.wait_for_acceptance()

# Calling contract's function doesn't create a new transaction, you get the function's result.
(saved,) = await contract.functions["get"].call(key)
# saved = 7 now
```

To check if invoke succeeded use `wait_for_acceptance` on InvokeResult and get its status.

Although asynchronous API is recommended, you can also use Contract’s synchronous API:

```python
from starknet_py.contract import Contract
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping

contract_address = (
    "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"
)

key = 1234
contract = Contract.from_address_sync(address=contract_address, provider=account)

resource_bounds = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
)
invocation = contract.functions["put"].invoke_v3_sync(key, 7, resource_bounds=resource_bounds)
invocation.wait_for_acceptance_sync()

(saved,) = contract.functions["get"].call_sync(key)  # 7
```

Contract automatically serializes values to Cairo calldata. This includes adding array lengths automatically. 
See more info in [Serialization](https://starknetpy.readthedocs.io/en/latest/guide/serialization.html#serialization).

Quickstart in docs - click [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).
