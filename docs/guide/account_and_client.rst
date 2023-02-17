Account and Client
==================

Account details
---------------

:ref:`Account` provides a simple way of executing transactions. To send one with few calls
just prepare calls through contract interface and send it with Account.execute method.

Here is an example:

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_account_details.py
    :language: python
    :dedent: 4


FullNodeClient usage
--------------------

Use a :ref:`FullNodeClient` to interact with services providing `Starknet rpc interface <https://github.com/starkware-libs/starknet-specs/blob/606c21e06be92ea1543fd0134b7f98df622c2fbf/api/starknet_api_openrpc.json>`_
like `Pathfinder Full Node <https://github.com/eqlabs/pathfinder>`_ or starknet-devnet. starknet.py provides uniform interface for
both gateway and full node client - usage is exactly the same as gateway client minus some optional
parameters.

Using own full node allows for querying Starknet with better performance.
Since gateway will be deprecated at some point in the future, having ``FullNodeClient`` with interface uniform with that of ``GatewayClient``
will allow for simple migration for starknet.py users.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_full_node_client.py
    :language: python
    :dedent: 4


Handling client errors
-----------------------
You can use :class:`starknet_py.net.client_errors.ClientError` to catch errors from invalid requests:

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_handling_client_errors.py
    :language: python
    :dedent: 4


Custom nonce logic
------------------

By default, :ref:`Account` calls Starknet for nonce every time a new transaction is signed or executed.
This is okay for most users, but in case your applications needs to pre-sign multiple transactions
for execution, deals with high amount of transactions or just needs to support different nonce
logic, it is possible to so with :ref:`Account`. Simply overwrite the
:meth:`~starknet_py.net.account.account.Account.get_nonce` method with your own logic.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_custom_nonce.py
    :language: python
    :dedent: 4
