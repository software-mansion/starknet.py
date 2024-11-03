Using existing contracts
========================

Existing contracts
------------------

Although it is possible to use :ref:`Client` to interact with contracts, it requires translating python values into Cairo
values. Contract offers that and some other utilities.

Let's say we have a contract with this interface:

.. literalinclude:: ../../starknet_py/tests/e2e/docs/guide/test_using_existing_contracts.py
    :language: python
    :start-after: docs-abi: start
    :end-before: docs-abi: end


This is how we can interact with it:

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_using_existing_contracts.py
    :language: python
    :dedent: 4


Raw contract calls
------------------

If you do not have ABI statically, but you know the interface of the contract on Starknet, you can make a raw call:

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_using_existing_contracts.py
    :language: python
    :dedent: 4
    :start-after: docs-raw-call: start
    :end-before: docs-raw-call: end


Fees
----

.. currentmodule:: starknet_py.contract

Starknet.py requires you to specify amount of Wei (for V1 transaction) or Fri (for V3 transaction) you
are willing to pay when executing either :meth:`~ContractFunction.invoke_v1` or :meth:`~ContractFunction.invoke_v3` transactions.
Alternatively, you can estimate fee automatically, as described in the :ref:`automatic-fee-estimation` section below.

.. code-block:: python

    await contract.functions["put"].invoke_v1(k, v, max_fee=5000)

The ``max_fee`` argument can be also defined in :meth:`~ContractFunction.prepare_invoke_v1`. Subsequently, the :meth:`~PreparedFunctionInvokeV1.invoke` method on a prepared call can be used either with ``max_fee`` omitted or with its value overridden.
The same behavior applies to :meth:`~ContractFunction.prepare_invoke_v3` and ``resource_bounds``.

.. code-block:: python

    prepared_call = contract.function["put"].prepare_invoke_v1(k, v, max_fee=5000)
    await prepared_call.invoke()
    # or max_fee can be overridden
    await prepared_call.invoke(max_fee=10000)

.. warning::

    For V1 transactions if ``max_fee`` is not specified at any step it will default to ``None``,
    and will raise an exception when invoking a transaction, unless `auto_estimate` is specified and is set to `True`. The same applies to ``resource_bounds`` and V3 transactions.

Please note you will need to have enough Wei (for V1 transaction) or Fri (for V3 transaction) in your Starknet account otherwise
transaction will be rejected.

Fee estimation
--------------

You can estimate required amount of fee that will need to be paid for transaction
using :meth:`PreparedFunctionInvoke.estimate_fee() <starknet_py.contract.PreparedFunctionInvoke.estimate_fee>`

.. code-block:: python

    await contract.functions["put"].prepare_invoke_v1(k, v).estimate_fee()

.. _automatic-fee-estimation:

Automatic fee estimation
------------------------

For testing purposes it is possible to enable automatic fee estimation when making a transaction. Starknet.py will then call :meth:`~starknet_py.net.full_node_client.FullNodeClient.estimate_fee`
internally and use the returned value, multiplied by ``1.5`` to mitigate fluctuations in price, as a ``max_fee`` for V1 transactions. For V3 transactions,
``max_amount`` will be multiplied by ``1.1``, and ``max_price_per_unit`` by ``1.5``.

.. code-block:: python

    await contract.functions["put"].invoke_v1(k, v, auto_estimate=True)

.. warning::

    It is strongly discouraged to use automatic fee estimation in production code as it may lead to unexpectedly high fee.

.. note::
    For V1 transactions it is possible to configure the value by which the estimated fee is multiplied,
    by changing ``ESTIMATED_FEE_MULTIPLIER`` in :class:`~starknet_py.net.account.account.Account`. The same applies to
    ``ESTIMATED_AMOUNT_MULTIPLIER`` and ``ESTIMATED_UNIT_PRICE_MULTIPLIER`` for V3 transactions.

Account and Client interoperability
-----------------------------------

.. currentmodule:: starknet_py.contract

:ref:`Contract` methods have been designed to be compatible with :ref:`Account` and :ref:`Client`.

:ref:`PreparedFunctionInvokeV1` and :ref:`PreparedFunctionInvokeV3` returned by :meth:`ContractFunction.prepare_invoke_v1` and :meth:`ContractFunction.prepare_invoke_v3` respectively can be used in Account methods to create Invoke transactions.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_contract_account_compatibility.py
    :language: python
    :dedent: 4


Similarly, :ref:`PreparedFunctionCall` returned by :meth:`ContractFunction.prepare_call` can be used in :meth:`Client.call_contract() <starknet_py.net.client.Client.call_contract>`

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_contract_client_compatibility.py
    :language: python
    :dedent: 4
