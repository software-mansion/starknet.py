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

You can see all Gateway Client's methods :obj:`here <starknet_py.net.gateway_client.GatewayClient>`.

Using FullNodeClient
--------------------
FullNodeClient is a client which interacts with a StarkNet full node like `pathfinder <https://github.com/eqlabs/pathfinder>`_.
For now API only supports read operations - it will change in the future along with full node write support.
As with GatewayClient, there is both synchronous and asynchronous API available.
Usage is a little different than the GatewayClient, see below:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_full_node_client.py
    :language: python
    :lines: 12-15,21-22
    :dedent: 4

You can see all Gateway Client's methods :obj:`here <starknet_py.net.full_node_client.FullNodeClient>`.

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
    :lines: 15-18,22-25,29-47
    :dedent: 4

Using Contract
--------------
:obj:`Contract <starknet_py.contract.Contract>` makes interacting with contracts deployed on Starknet much easier:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_contract.py
    :language: python
    :lines: 16-21,28-34,46-48,54-71
    :dedent: 4

Although asynchronous API is recommended, you can also use Contract's synchronous API:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_api.py
    :language: python
    :lines: 15-22,35-42
    :dedent: 4
