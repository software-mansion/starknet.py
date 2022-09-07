<div align="center">
    <img src="https://raw.githubusercontent.com/software-mansion/starknet.py/master/graphic.png" alt="starknet.py"/>
</div>
<h2 align="center">StarkNet SDK for Python</h2>

<div align="center">

[![codecov](https://codecov.io/gh/software-mansion/starknet.py/branch/master/graph/badge.svg?token=3E54E8RYSL)](https://codecov.io/gh/software-mansion/starknet.py)
[![pypi](https://img.shields.io/pypi/v/starknet.py)](https://pypi.org/project/starknet.py/)
[![build](https://img.shields.io/github/workflow/status/software-mansion/starknet.py/format%20-%3E%20lint%20-%3E%20test)](https://github.com/software-mansion/starknet.py/actions)
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

## ⚙️ Installation
To install this package run

```
pip install starknet.py
```

or using Poetry:

```
poetry add starknet.py
```

## ▶️ Example usage
### Asynchronous API
This is the recommended way of using the SDK.

```python
from starknet_py.contract import Contract
from starknet_py.net.client import Client

key = 1234
contract = await Contract.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client("testnet"))
invocation = await contract.functions["set_value"].invoke(key, 7)
await invocation.wait_for_acceptance()

(saved,) = await contract.functions["get_value"].call(key) # 7
```

### Synchronous API
You can access synchronous world with `_sync` postfix.

```python
from starknet_py.contract import Contract
from starknet_py.net.client import Client

key = 1234
contract = Contract.from_address_sync("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client("testnet"))
invocation = contract.functions["set_value"].invoke_sync(key, 7)
invocation.wait_for_acceptance_sync()

(saved,) = contract.functions["get_value"].call_sync(key) # 7
```

For more examples click [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).
