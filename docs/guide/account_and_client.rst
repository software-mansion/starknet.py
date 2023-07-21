Account and Client
==================

Executing transactions
----------------------

To execute transactions on Starknet, use :meth:`~starknet_py.net.account.account.Account.execute` method from :ref:`Account` interface.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_executing_transactions.py
    :language: python
    :dedent: 4

Creating transactions without executing them
--------------------------------------------

Alongside the simpler :meth:`~starknet_py.net.account.account.Account.execute`,
Account also provides a way of creating signed transaction without sending them.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_account_sign_without_execute.py
    :language: python
    :dedent: 4

Multicall
---------

There is a possibility to execute an Invoke transaction containing multiple calls.
Simply pass a list of calls to :meth:`~starknet_py.net.account.account.Account.execute` method.
Note that the nonce will be bumped only by 1.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_multicall.py
    :language: python
    :dedent: 4

.. note::
    If you want to create a **read-only** multicall that does not change on-chain state, check out `this cairo contract made by Argent <https://github.com/argentlabs/argent-contracts-starknet/blob/d2e4365ff1005e03c5575b5a0db48060096cf391/contracts/lib/Multicall.cairo>`_, that implements an endpoint allowing for such behaviour.

.. warning::

    Do not pass arbitrarily large number of calls in one batch. Starknet rejects the transaction when it happens, like `here <https://testnet-2.starkscan.co/tx/0x20440925a18ba8911f2fe2bbbcb64511ca5f3d7bffaa036ea3eda0f9cef26f6#overview>`_.



FullNodeClient usage
--------------------

Use a :ref:`FullNodeClient` to interact with services providing `Starknet RPC interface <https://github.com/starkware-libs/starknet-specs/blob/606c21e06be92ea1543fd0134b7f98df622c2fbf/api/starknet_api_openrpc.json>`_
like `Pathfinder <https://github.com/eqlabs/pathfinder>`_,
`Papyrus <https://github.com/starkware-libs/papyrus>`_, `Juno <https://github.com/NethermindEth/juno>`_
or `starknet-devnet <https://github.com/0xSpaceShard/starknet-devnet>`_.
Using own full node allows for querying Starknet with better performance.

Since GatewayClient is deprecated and will be removed at some point in the future, having ``FullNodeClient``
with interface uniform with that of ``GatewayClient`` will allow for simple migration for starknet.py users.

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
