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

Starknet.py requires you to specify amount of Wei (for V1 transaction) or Fri (for V3 transaction) you
are willing to pay when executing either ``.invoke_v1()`` or ``.invoke_v3()`` transactions. It's also possible to optionally define the transaction fee
when preparing function calls with ``.prepare_invoke_v1()`` or ``.prepare_invoke_v3()``.

.. code-block:: python

    await contract.functions["put"].invoke_v1(k, v, max_fee=5000)

When max_fee is specified when preparing a call, you can invoke it without ``max_fee``. It works similarly for ``l1_resource_bounds`` and ``prepare_invoke_v3()``.

.. code-block:: python

    prepared_call = contract.function["put"].prepare_invoke_v1(k, v, max_fee=5000)
    await prepared_call.invoke()

.. warning::

    For V1 transactions if ``max_fee`` is not specified at any step it will default to ``None``,
    and will raise an exception when invoking a transaction. The same applies to ``l1_resource_bounds`` and V3 transactions.

Please note you will need to have enough Wei (for V1 transaction) or Fri (for V3 transaction) in your Starknet account otherwise
transaction will be rejected.

Fee estimation
--------------

You can estimate required amount of fee that will need to be paid for transaction
using :meth:`PreparedFunctionInvoke.estimate_fee() <starknet_py.contract.PreparedFunctionInvoke.estimate_fee>`

.. code-block:: python

    await contract.functions["put"].prepare_invoke_v1(k, v).estimate_fee()


Automatic fee estimation
------------------------

For testing purposes it is possible to enable automatic fee estimation when making
a transaction. Starknet.py will then use ``estimate_fee()`` internally and use value
returned by it multiplied by ``1.5`` as a ``max_fee`` for V1 transactions. For V3 transactions,
``max_amount`` will be multiplied by ``1.1``, and ``max_price_per_unit`` by ``1.5``.

.. warning::

    Do not use automatic fee estimation in production code! It may lead to
    very high fees paid as the amount returned by ``estimate_fee()`` may be arbitrarily large.

.. code-block:: python

    await contract.functions["put"].invoke_v1(k, v, auto_estimate=True)


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
