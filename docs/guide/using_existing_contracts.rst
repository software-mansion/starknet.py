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

starknet.py requires you to specify amount of Wei you
are willing to pay either when making ``.invoke()`` transactions or when preparing
function calls with ``.prepare()``.

.. code-block:: python

    await contract.functions["put"].invoke(k, v, max_fee=5000)

When max_fee is specified when preparing a call, you can invoke it without
``max_fee``.

.. code-block:: python

    prepared_call = contract.function["put"].prepare(k, v, max_fee=5000)
    await prepared_call.invoke()

.. warning::

    If ``max_fee`` is not specified at any step it will default to ``None``,
    and will raise an exception when invoking a transaction.

Please note you will need to have enough Wei in your Starknet account otherwise
transaction will be rejected.

Fee estimation
--------------

You can estimate required amount of fee that will need to be paid for transaction
using :meth:`PreparedFunctionCall.estimate_fee() <starknet_py.contract.PreparedFunctionCall.estimate_fee>`

.. code-block:: python

    await contract.functions["put"].prepare(k, v, max_fee=5000).estimate_fee()


Automatic fee estimation
------------------------

For testing purposes it is possible to enable automatic fee estimation when making
a transaction. starknet.py will then use ``estimate_fee()`` internally and use value
returned by it multiplied by ``1.5`` as a ``max_fee``.

.. warning::

    Do not use automatic fee estimation in production code! It may lead to
    very high fees paid as the amount returned by ``estimate_fee()`` may be arbitrarily large.

.. code-block:: python

    await contract.functions["put"].invoke(k, v, auto_estimate=True)


.. note::
    It is possible to configure the value by which the estimated fee is multiplied,
    by changing ``ESTIMATED_FEE_MULTIPLIER`` in :class:`~starknet_py.net.account.account.Account`.

Account and Client interoperability
-----------------------------------

.. currentmodule:: starknet_py.contract

:ref:`Contract` methods have been designed to be
compatible with :ref:`Account` and :ref:`Client`.

:ref:`PreparedFunctionCall` returned by :meth:`ContractFunction.prepare` can be used in Account methods to create Invoke transactions.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_contract_account_compatibility.py
    :language: python
    :dedent: 4

It can also be used in :meth:`Client.call_contract() <starknet_py.net.client.Client.call_contract>`

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_contract_client_compatibility.py
    :language: python
    :dedent: 4
