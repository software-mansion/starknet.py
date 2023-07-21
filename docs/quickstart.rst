Quickstart
==========

Using FullNodeClient
--------------------
A :ref:`Client` is a facade for interacting with Starknet.
:ref:`FullNodeClient` is a client which interacts
with a Starknet full nodes like `Pathfinder <https://github.com/eqlabs/pathfinder>`_,
`Papyrus <https://github.com/starkware-libs/papyrus>`_ or `Juno <https://github.com/NethermindEth/juno>`_.
It supports read and write operations, like querying the blockchain state or adding new transactions.

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_using_full_node_client.py
    :language: python
    :dedent: 4

The default interface is asynchronous. Although it is the recommended way of using starknet.py, you can also use a
synchronous version. It might be helpful to play with Starknet directly in python interpreter.

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_full_node_client.py
    :language: python
    :dedent: 4

You can check out all of the FullNodeClient's methods here: :ref:`FullNodeClient`.

Using GatewayClient
-------------------

.. warning::

    Gateway / Feeder Gateway API will become deprecated in the future. As a result, GatewayClient won't work and will
    eventually be removed. Consider migrating to :ref:`FullNodeClient`.

:ref:`GatewayClient` will make requests directly to Starknet sequencer through `gateway` or `feeder_gateway` endpoints.
It can be used to either query the blockchain state or add new transactions.
It requires information about used network:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_using_gateway_client.py
    :language: python
    :dedent: 4

It also has async/sync interface:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_gateway_client.py
    :language: python
    :dedent: 4

You can check out all of the GatewayClient's methods here: :ref:`GatewayClient`.


Creating Account
----------------------

:obj:`Account <starknet_py.net.account.account.Account>` is the default implementation of :obj:`BaseAccount <starknet_py.net.account.base_account.BaseAccount>` interface.
It supports an account contract which proxies the calls to other contracts on Starknet.

Account can be created in two ways:

* By constructor (address, key_pair and net must be known).
* By static method ``Account.deploy_account``

There are some examples how to do it:

.. codesnippet:: ../starknet_py/tests/e2e/docs/quickstart/test_creating_account.py
    :language: python
    :dedent: 4

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
