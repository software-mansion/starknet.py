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
[![Read FAQ](https://img.shields.io/badge/Ask%20Question-Read%20FAQ-000000)](https://www.newton.so/view?tags=starknetpy)
</div>

## 📘 Documentation

- [Installation](https://starknetpy.rtfd.io/en/latest/installation.html)
- [Quickstart](https://starknetpy.rtfd.io/en/latest/quickstart.html)
- [Guide](https://starknetpy.rtfd.io/en/latest/guide.html)
- [API](https://starknetpy.rtfd.io/en/latest/api.html)
- [FAQ](https://www.newton.so/view?tags=starknetpy)

## ⚙️ Installation

Installation varies between operating systems.

[See our documentation on complete instructions](https://starknetpy.rtfd.io/en/latest/installation.html)

## ▶️ Example usage

### Asynchronous API

This is the recommended way of using the SDK.

```python
from starknet_py.contract import Contract
from starknet_py.net.gateway_client import GatewayClient

key = 1234
contract = await Contract.from_address(
    address="0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b",
    client=GatewayClient("testnet"),
)
(value,) = await contract.functions["get_value"].call(key)
```

### Synchronous API

You can access synchronous world with `_sync` postfix.

```python
from starknet_py.contract import Contract
from starknet_py.net.gateway_client import GatewayClient

key = 1234
contract = Contract.from_address_sync(
    address="0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b",
    client=GatewayClient("testnet"),
)
(value,) = contract.functions["get_value"].call_sync(key)
```

For more examples click [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).

## ❓Questions / FAQ

Questions are welcome!
If you have any questions regarding Starknetpy, feel free to ask them using [Newton](https://www.newton.so/view?tags=starknetpy).

### FAQ
- [How to get the contract ABI using Starknet.Py?](https://www.newton.so/view/6396da0279d6fc052ee89836)
- [How to deploy a contract through starknet.py?](https://www.newton.so/view/639988001b2d6ff34ff7c303)
- [How to send tokens through StarkNet.py?](https://www.newton.so/view/639c3115c2fdce3d188d0293)
- [How to use await in StarkNet.py?](https://www.newton.so/view/639c307fc2fdce3d188d0292)
- [What does this error means? (AssertionError: assert_not_zero failed: 0 = 0.)](https://www.newton.so/view/639c295efd8cf7a2c25adbc8)
- [How to use Argent (or any from the main providers) account in the StarkNet.py?](https://www.newton.so/view/639c2b32fd8cf7a2c25adbc9)
- [StarknetPy Error in get_balance_sync (StarknetErrorCode.ENTRY_POINT_NOT_FOUND_IN_CONTRACT)](https://www.newton.so/view/63983e3fa99cb007b4a247c6)
