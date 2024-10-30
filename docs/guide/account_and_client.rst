Account and Client
==================

Executing transactions
----------------------

To execute transactions on Starknet, use :meth:`~starknet_py.net.account.account.Account.execute_v1` or :meth:`~starknet_py.net.account.account.Account.execute_v3` methods from :ref:`Account` interface.
These methods will send :class:`~starknet_py.net.models.InvokeV1` and :class:`~starknet_py.net.models.InvokeV3` transactions respectively. To read about differences between transaction versions please visit `transaction types <https://docs.starknet.io/documentation/architecture_and_concepts/Network_Architecture/transactions>`_ from the Starknet docs.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_executing_transactions.py
    :language: python
    :dedent: 4

Transaction Fee
---------------

All methods within the :ref:`Account` that involve on-chain modifications require either specifying a maximum transaction fee or using auto estimation.
In the case of V1 and V2 transactions, the transaction fee, denoted in Wei, is configured by the ``max_fee`` parameter.
For V3 transactions, however, the fee is expressed in Fri and is determined by the ``resource_bounds`` parameter.
To enable auto estimation, set the ``auto_estimate`` parameter to ``True``.

.. code-block:: python

    resp = await account.execute_v1(calls=call, auto_estimate=True)

.. warning::

    It is strongly discouraged to use automatic fee estimation in production code as it may lead to an unexpectedly high fee.

The returned estimated fee is multiplied by ``1.5`` for V1 and V2 transactions to mitigate fluctuations in price.
For V3 transactions, ``max_amount`` and ``max_price_per_unit`` are scaled by ``1.5`` and ``1.5`` respectively.

.. note::
    It is possible to configure the value by which the estimated fee is multiplied,
    by changing ``ESTIMATED_FEE_MULTIPLIER`` for V1 and V2 transactions in :class:`~starknet_py.net.account.account.Account`.
    The same applies to ``ESTIMATED_AMOUNT_MULTIPLIER`` and ``ESTIMATED_UNIT_PRICE_MULTIPLIER`` for V3 transactions.

The fee for a specific transaction or list of transactions can be also estimated using the :meth:`~starknet_py.net.account.account.Account.estimate_fee` of the :ref:`Account` class.

Creating transactions without executing them
--------------------------------------------

Account also provides a way of creating signed transaction without sending them.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_account_sign_without_execute.py
    :language: python
    :dedent: 4

Multicall
---------

There is a possibility to execute an Invoke transaction containing multiple calls.
Simply pass a list of calls to :meth:`~starknet_py.net.account.account.Account.execute_v1` or :meth:`~starknet_py.net.account.account.Account.execute_v3` methods.
Note that the nonce will be bumped only by 1.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_multicall.py
    :language: python
    :dedent: 4

.. note::
    If you want to create a **read-only** multicall that does not change on-chain state, check out `this cairo contract made by Argent <https://github.com/argentlabs/argent-contracts-starknet/blob/d2e4365ff1005e03c5575b5a0db48060096cf391/contracts/lib/Multicall.cairo>`_, that implements an endpoint allowing for such behaviour.

.. warning::

    Do not pass arbitrarily large number of calls in one batch. Starknet rejects the transaction when it happens.

FullNodeClient usage
--------------------

Use a :ref:`FullNodeClient` to interact with services providing `Starknet RPC interface <https://github.com/starkware-libs/starknet-specs/blob/606c21e06be92ea1543fd0134b7f98df622c2fbf/api/starknet_api_openrpc.json>`_
like `Pathfinder <https://github.com/eqlabs/pathfinder>`_,
`Papyrus <https://github.com/starkware-libs/papyrus>`_, `Juno <https://github.com/NethermindEth/juno>`_
or `starknet-devnet <https://github.com/0xSpaceShard/starknet-devnet>`_.
Using own full node allows for querying Starknet with better performance.

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
This is okay for most users, but in case your application needs to pre-sign multiple transactions
for execution, deals with high amount of transactions or just needs to support different nonce
logic, it is possible to do so with :ref:`Account`. Simply overwrite the
:meth:`~starknet_py.net.account.account.Account.get_nonce` method with your own logic.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_custom_nonce.py
    :language: python
    :dedent: 4
