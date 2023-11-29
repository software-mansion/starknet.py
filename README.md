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

### Asynchronous API

This is the recommended way of using the SDK.

```python
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

contract = await Contract.from_address(
    address="0x06689f1bf69af5b8e94e5ab9778c885b37c593d1156234eb423967621f596e73",
    client=FullNodeClient(node_url="https://your.node.url"),
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
    client=FullNodeClient(node_url="https://your.node.url"),
)
(value,) = contract.functions["get_balance"].call_sync()
```

For more examples click [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).
