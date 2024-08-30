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

## ▶️ Example usage

### Account setup

To start interacting with Starknet you need to have an account. Using the starknet.py you can create a new account 
or load an existing one. You can also create an account using [sncast](https://foundry-rs.github.io/starknet-foundry/starknet/index.html) 
tool - it automatically saves the account in the file. 

You can read about account creation using starknet.py [here](https://starknetpy.readthedocs.io/en/latest/account_creation.html#account-creation)
```python
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models.chains import StarknetChainId

# Define the client to be used to interact with Starknet
client = FullNodeClient(node_url="https://your.node.url")

# You can initialize the account class using your private_key and contract address
account = Account(
            client=client,
            address="0x71429387",
            key_pair=KeyPair.from_private_key("0x1424351"),
            chain=StarknetChainId.SEPOLIA
)

balance = account.get_balance_sync() # Account class automatically generates synchronous versions of methods. 
```

### Calling contract

```python
from starknet_py.contract import Contract

contract = Contract.from_address_sync(
    address="0x05dea4f027d68c5f16e339d17cc9be17ac4cd6c34433eb816e557ae858d2de78",
    provider=client,
)
resp = contract.functions["all"].call_sync()
```
### Executing transactions
    
```python
from starknet_py.net.client_models import Call

call = Call(
    contract.address,
    get_selector_from_name("like"),
    [1225946354835439842674],
)

invoke_tx = account.sign_invoke_v3_sync(calls=call, auto_estimate=True)
response = client.send_transaction_sync(invoke_tx)

```

### Asynchronous API

This is the recommended way of using the SDK.

```python
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

contract = await Contract.from_address(
    address="0x06689f1bf69af5b8e94e5ab9778c885b37c593d1156234eb423967621f596e73",
    provider=FullNodeClient(node_url="https://your.node.url"),
)
(value,) = await contract.functions["get_balance"].call()
```

### Synchronous API

You can access synchronous world with `_sync` postfix.

```python
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

contract = Contract.from_address_sync(
    address="0x06689f1bf69af5b8e94e5ab9778c885b37c593d1156234eb423967621f596e73",
    provider=FullNodeClient(node_url="https://your.node.url"),
)
(value,) = contract.functions["get_balance"].call_sync()
```

For more examples click [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).
