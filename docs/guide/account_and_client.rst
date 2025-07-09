Account and Client
==================

Executing transactions
----------------------

To execute transactions on Starknet, use :meth:`~starknet_py.net.account.account.Account.execute_v3` method from :ref:`Account` interface, which will send :class:`~starknet_py.net.models.InvokeV3` transaction.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_executing_transactions.py
    :language: python
    :dedent: 4

Transaction Fee
---------------

All methods within the :ref:`Account` that involve on-chain modifications require either specifying a maximum transaction fee or using auto estimation.
For V3 transaction, the fee is expressed in Fri and is determined by the ``resource_bounds`` parameter.
To enable auto estimation, set the ``auto_estimate`` parameter to ``True``.

.. code-block:: python

    resp = await account.execute_v3(calls=call, auto_estimate=True)

.. warning::

    It is strongly discouraged to use automatic fee estimation in production code as it may lead to an unexpectedly high fee.

The returned estimated fee (``max_amount`` and ``max_price_per_unit``) is multiplied by ``1.5`` to mitigate fluctuations in price.

.. note::
    It is possible to configure the value by which the estimated fee is multiplied,
    by changing ``ESTIMATED_AMOUNT_MULTIPLIER`` and ``ESTIMATED_UNIT_PRICE_MULTIPLIER`` in :class:`~starknet_py.net.account.account.Account`.

The fee for a specific transaction or list of transactions can be also estimated using the :meth:`~starknet_py.net.account.account.Account.estimate_fee` of the :ref:`Account` class.

Transaction Tips
----------------

Until Starknet 0.14.0, transactions were processed in FIFO order.
Starting from this version, it is possible to include a *tip* with the transaction fee to incentivize it being placed in an earlier block.

Starknet.py supports this mechanism in several interfaces.

.. code-block:: python

    resp = await account.execute_v3(calls=call, tip=12345)

Creating transactions without executing them
--------------------------------------------

Account also provides a way of creating signed transaction without sending them.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_account_sign_without_execute.py
    :language: python
    :dedent: 4

Outside execution
-----------------

Outside execution allows a protocol to submit a transaction on behalf of another account. This feature is implemented according to `SNIP-9 <https://github.com/starknet-io/SNIPs/blob/main/SNIPS/snip-9.md>`_.

Account also provides a way of signing transaction which later can be execute by another account. Signer does not need to be funded with tokens as executor will pay the fee.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_account_sign_outside_transaction.py
    :language: python
    :dedent: 4

Multicall
---------

There is a possibility to execute an Invoke transaction containing multiple calls.
Simply pass a list of calls to :meth:`~starknet_py.net.account.account.Account.execute_v3` method.
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
