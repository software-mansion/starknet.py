Quickstart
==========

Using GatewayClient
-------------------
A client (i.e. :obj:`GatewayClient <starknet_py.net.gateway_client.GatewayClient>`, :obj:`FullNodeClient <starknet_py.net.full_node_client.FullNodeClient>`) is a facade for interacting with Starknet.
Gateway client will make requests directly to starknet sequencer through `gateway` or `feeder_gateway` endpoints.
It can be used to either query the blockchain state or add new transactions.
It requires information about used network:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_gateway_client.py
    :language: python
    :lines: 8-29
    :dedent: 4

The default interface is asynchronous. Although it is the recommended way of using Starknet.py, you can also use a
synchronous version. It might be helpful to play with Starknet directly in python interpreter.

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_gateway_client.py
    :language: python
    :lines: 11-14
    :dedent: 4

You can see all Gateway Client's methods :ref:`GatewayClient`.

Using FullNodeClient
--------------------
FullNodeClient is a client which interacts with a StarkNet full node like `pathfinder <https://github.com/eqlabs/pathfinder>`_.
For now API only supports read operations - it will be changed in future versions.
As with GatewayClient, there is both synchronous and asynchronous API available.

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_full_node_client.py
    :language: python
    :lines: 14-17,27-28
    :dedent: 4

You can see all Full Node Client's methods :ref:`FullNodeClient`.

Creating AccountClient
----------------------

:obj:`AccountClient <starknet_py.net.account.account_client.AccountClient>` is an extension of a regular client. It leverages `OpenZeppelin's Cairo contracts <https://github.com/OpenZeppelin/cairo-contracts>`_ to create an account contract which proxies (and signs) the calls to other contracts on Starknet.

AccountClient can be created in two ways:

* By constructor (address, key_pair and net must be known).
* By static method AccountClient.create_account.

There are some examples how to do it:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_creating_account_client.py
    :language: python
    :lines: 10-15,19-37
    :dedent: 4

Using AccountClient
-------------------

Example usage:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_account_client.py
    :language: python
    :lines: 14-17,21-24,28-58
    :dedent: 4

Using Contract
--------------
:obj:`Contract <starknet_py.contract.Contract>` makes interacting with contracts deployed on Starknet much easier:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_contract.py
    :language: python
    :lines: 15-20,25-31,42-44,50-67
    :dedent: 4

Although asynchronous API is recommended, you can also use Contract's synchronous API:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_api.py
    :language: python
    :lines: 13-20,33-40
    :dedent: 4
