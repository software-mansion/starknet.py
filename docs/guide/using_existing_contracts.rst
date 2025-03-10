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

Starknet.py requires you to specify amount of Fri that you are willing to pay when executing :meth:`~ContractFunction.invoke_v3`.
Alternatively, you can estimate fee automatically, as described in the :ref:`automatic-fee-estimation` section below.

.. code-block:: python

    await contract.functions["put"].invoke_v3(k, v, resource_bounds=ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
        l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    ))

The ``resource_bounds`` argument can be also defined in :meth:`~ContractFunction.prepare_invoke_v3`. Subsequently, the :meth:`~PreparedFunctionInvokeV3.invoke` method on a prepared call can be used either with ``resource_bounds`` omitted or with its value overridden.

.. code-block:: python

    prepared_call = contract.function["put"].prepare_invoke_v3(k, v, resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        ))
    await prepared_call.invoke()
    # or resource_bounds can be overridden
    await prepared_call.invoke(resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        ))

.. warning::

    If ``resource_bounds`` is not specified at any step it will default to ``None``,
    and will raise an exception when invoking a transaction, unless `auto_estimate` is specified and is set to `True`.

Please note you will need to have enough Fri in your Starknet account otherwise
transaction will be rejected.

Fee estimation
--------------

You can estimate required amount of fee that will need to be paid for transaction
using :meth:`PreparedFunctionInvoke.estimate_fee() <starknet_py.contract.PreparedFunctionInvoke.estimate_fee>`

.. code-block:: python

    await contract.functions["put"].prepare_invoke_v3(k, v).estimate_fee()

.. _automatic-fee-estimation:

Automatic fee estimation
------------------------

For testing purposes it is possible to enable automatic fee estimation when making a transaction. Starknet.py will then call :meth:`~starknet_py.net.full_node_client.FullNodeClient.estimate_fee`
internally and use the returned value. ``max_amount`` and ``max_price_per_unit`` will be multiplied by ``1.5``.

.. code-block:: python

    await contract.functions["put"].invoke_v3(k, v, auto_estimate=True)

.. warning::

    It is strongly discouraged to use automatic fee estimation in production code as it may lead to unexpectedly high fee.

.. note::
    It is possible to configure the value by which the estimated fee is multiplied,
    by changing ``ESTIMATED_AMOUNT_MULTIPLIER`` and ``ESTIMATED_UNIT_PRICE_MULTIPLIER``.

Account and Client interoperability
-----------------------------------

.. currentmodule:: starknet_py.contract

:ref:`Contract` methods have been designed to be compatible with :ref:`Account` and :ref:`Client`.

:ref:`PreparedFunctionInvokeV3` returned by :meth:`ContractFunction.prepare_invoke_v3` can be used in Account methods to create invoke transaction.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_contract_account_compatibility.py
    :language: python
    :dedent: 4


Similarly, :ref:`PreparedFunctionCall` returned by :meth:`ContractFunction.prepare_call` can be used in :meth:`Client.call_contract() <starknet_py.net.client.Client.call_contract>`

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_contract_client_compatibility.py
    :language: python
    :dedent: 4
