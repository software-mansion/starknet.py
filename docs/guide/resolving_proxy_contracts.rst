Resolving proxy contracts
=========================

.. note::
    If you know the abi of the contract, **always prefer** creating Contract directly from constructor.

    :meth:`Contract.from_address <starknet_py.contract.Contract.from_address>` must perform some calls to StarkNet to get an abi of the contract.

Resolving proxies is a powerful feature of Starknet.py. If your contract is a proxy to some implementation, you can use
high-level :meth:`Contract.from_address <starknet_py.contract.Contract.from_address>` method to get a contract instance.

:meth:`Contract.from_address <starknet_py.contract.Contract.from_address>` works with contracts which are not proxies, so it is the most universal method of getting
a contract not knowing the abi.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_resolving_proxies.py
    :language: python
    :dedent: 4
    :start-after: docs-1: start
    :end-before: docs-1: end


ProxyChecks
-----------

Since the Proxy contracts on StarkNet can have different implementations, as every user can define their custom implementation, there is no single way of checking if some contract is a Proxy contract.

There are two main ways of proxying a contract on StarkNet:
 - forward the calls using ``library_call`` and ``class_hash`` of proxied contract
 - forward the calls using ``delegate_call`` and ``address`` of proxied contract

:meth:`Contract.from_address <starknet_py.contract.Contract.from_address>` uses ``proxy_checks`` to fetch the ``implementation`` (address or class hash) of the proxied contract.

**ProxyCheck** checks whether the contract is a Proxy contract.
It does that by trying to get the ``address`` or ``class_hash`` of the implementation.

By default, ``proxy_config`` uses a configuration with two **ProxyChecks**:
 - ArgentProxyCheck - resolves `Argent Proxy <https://github.com/argentlabs/argent-contracts-starknet/blob/b7c4af7462a461386d29551400b985832ba942de/contracts/upgrade/Proxy.cairo>`_.
 - OpenZeppelinProxyCheck - resolves `OpenZeppelin Proxy <https://github.com/OpenZeppelin/cairo-contracts/blob/d12abf335f5c778fd19d6f99e91c099b40865deb/src/openzeppelin/upgrades/presets/Proxy.cairo>`_.

It's possible to define own ProxyCheck implementation and later pass it to :meth:`Contract.from_address <starknet_py.contract.Contract.from_address>`, so it knows how to resolve the Proxy.

The **ProxyCheck** base class implements the following interface:

.. codesnippet:: ../../starknet_py/proxy/proxy_check.py
    :language: python
    :start-after: docs-proxy-check: start
    :end-before: docs-proxy-check: end

It has two methods:
 - `implementation_address` - returns the `address` of the proxied contract (implement this if your Proxy contract uses the `address` of another contract as `implementation`)
 - `implementation_hash` - returns the `class_hash` of the proxied contract (implement this if your Proxy contract uses the `class_hash` of another contract as `implementation`)


Here is the complete example:

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_resolving_proxies.py
    :language: python
    :dedent: 4
    :start-after: docs-2: start
    :end-before: docs-2: end
