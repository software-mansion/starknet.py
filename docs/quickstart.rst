Quickstart
==========

Using GatewayClient
-------------------
A client (i.e. :obj:`GatewayClient <starknet_py.net.gateway_client.GatewayClient>`, :obj:`FullNodeClient <starknet_py.net.full_node_client.FullNodeClient>`) is a facade for interacting with Starknet.
Gateway client will make requests directly to starknet sequencer through `gateway` or `feeder_gateway` endpoints.
It can be used to either query the blockchain state or add new transactions.
It requires information about used network:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_using_gateway_client.py
    :language: python
    :dedent: 4

The default interface is asynchronous. Although it is the recommended way of using Starknet.py, you can also use a
synchronous version. It might be helpful to play with Starknet directly in python interpreter.

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_gateway_client.py
    :language: python
    :dedent: 4

You can see all Gateway Client's methods :ref:`GatewayClient`.

Using FullNodeClient
--------------------
FullNodeClient is a client which interacts with a StarkNet full node like `pathfinder <https://github.com/eqlabs/pathfinder>`_.
Like the GatewayClient, it supports read and write operations. Also as with GatewayClient,
there is both synchronous and asynchronous API available.

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_using_full_node_client.py
    :language: python
    :dedent: 4

You can see all Full Node Client's methods :ref:`FullNodeClient`.

Creating Account
----------------------

.. warning::

    ``AccountClient`` has been deprecated in favor of the new ``Account``.
    New ``Account`` doesn't implement a ``Client`` interface in favor of composition.
    We recommend migrating to new Account as ``AccountClient`` will be removed in the future.

:obj:`Account <starknet_py.net.account.account.Account>` is the default implementation of :obj:`BaseAccount <starknet_py.net.account.base_account.BaseAccount>` interface.
It supports an account contract which proxies the calls to other contracts on StarkNet.

Account can be created in two ways:

* By constructor (address, key_pair and net must be known).
* By static method ``Account.deploy_account``

There are some examples how to do it:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_creating_account.py
    :language: python
    :dedent: 4

.. note::

    Since 0.5.0 :obj:`AccountClient <starknet_py.net.account.account_client.AccountClient>` has `supported_tx_version` parameter.
    It is responsible for keeping an information about transaction version supported by the account. The `AccountClient`'s constructor
    takes `supported_tx_version` as an argument (it is set to 0 by default).

.. note::

    We encourage you to upgrade your accounts to ones supporting latest transaction version.

Using Account
-------------------

Example usage:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_using_account.py
    :language: python
    :dedent: 4

Using Contract
--------------
:obj:`Contract <starknet_py.contract.Contract>` makes interacting with contracts deployed on Starknet much easier:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_using_contract.py
    :language: python
    :dedent: 4

.. note::

    To check if invoke succeeds use wait_for_acceptance on InvokeResult and get its status.

Although asynchronous API is recommended, you can also use Contract's synchronous API:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_api.py
    :language: python
    :dedent: 4

.. note::

    Contract automatically serializes values to Cairo calldata. This includes adding array lengths automatically. See
    more info in :ref:`Serialization`.
