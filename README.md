<h1 align="center">✨🐍 starknet.py</h1>
<h2 align="center">StarkNet SDK for Python</h2>

<p align="center">

[![codecov](https://codecov.io/gh/software-mansion/starknet_python_sdk/branch/master/graph/badge.svg?token=3E54E8RYSL)](https://codecov.io/gh/software-mansion/starknet_python_sdk)
<a href="https://github.com/software-mansion/starknet_python_sdk/actions">
    <img src="https://img.shields.io/github/workflow/status/software-mansion/starknet_python_sdk/format -> lint -> test">
</a>
[![Documentation Status](https://readthedocs.org/projects/starknetpy/badge/?version=latest)](https://starknetpy.readthedocs.io/en/latest/?badge=latest)
<a href="https://github.com/seanjameshan/starknet.js/blob/main/LICENSE/">
    <img src="https://img.shields.io/badge/license-MIT-black">
</a>
<a href="https://github.com/software-mansion/starknet_python_sdk/stargazers">
    <img src='https://img.shields.io/github/stars/software-mansion/starknet_python_sdk?color=yellow' />
</a>
<a href="https://starkware.co/">
    <img src="https://img.shields.io/badge/powered_by-StarkWare-navy">
</a>

</p>

## 📘 Documentation
- [Installation](https://starknetpy.rtfd.io/en/latest/installation.html)
- [Quickstart](https://starknetpy.rtfd.io/en/latest/quickstart.html)
- [Guide](https://starknetpy.rtfd.io/en/latest/guide.html)
- [API](https://starknetpy.rtfd.io/en/latest/api.html)

## ▶️ Example usage
### Asynchronous API
This is the recommended way of using the SDK.
```
from starknet.contract import Contract
from starknet.net.client import Client

key = 1234
contract = await Contract.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client("testnet"))
invocation = await contract.functions["set_value"].invoke(key, 7)
await invocation.wait_for_acceptance()

(saved,) = await contract.functions["get_value"].call(key) # (7)
```

### Synchronous API
You can access synchronous world with `_sync` postfix.

```
from starknet.contract import Contract
from starknet.net.client import Client

key = 1234
contract = Contract.from_address_sync("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client("testnet"))
invocation = contract.functions["set_value"].invoke_sync(key, 7)
invocation.wait_for_acceptance_sync()

(saved,) = contract.functions["get_value"].call_sync(key) # 7
```

See more [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).