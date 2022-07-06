Migrating to starknet 0.8.0
===========================

Starknet 0.8.0 brought some changes to both its operation and internal APIs.
Due to that, your existing programs written using starknet.py will require some
changes to be able to work.

New account contract
--------------------

Starknet.py now uses a `account contract from cairo-lang library <https://github.com/starkware-libs/cairo-lang/blob/4e233516f52477ad158bc81a86ec2760471c1b65/src/starkware/starknet/third_party/open_zeppelin/Account.cairo>`_.
This changes internal transaction signing behavior.
Instead of generating a message to sign from multicall a transaction hash is signed.

Fees
----

Starknet 0.8.0 introduced support for fees, while they are not necessary yet,
starting this version starknet.py will require you to specify amount of Wei you
are willing to pay either when making ``.invoke()`` transactions or when preparing
function calls with ``.prepare()``.

.. note::

    StarkNet currently only supports ``max_fee > 0`` on testnet.

    Use ``max_fee = 0`` for transactions on mainnet.

before 0.8.0

.. code-block:: python

    await contract.functions["put"].invoke(k, v)

since 0.8.0

.. code-block:: python

    await contract.functions["put"].invoke(k, v, max_fee=5000)

when max_fee is specified when preparing a call, you can invoke it without
``max_fee``.

.. code-block:: python

    prepared_call = contract.function["put"].prepare(k, v, max_fee=5000)
    await prepared_call.invoke()

.. warning::

    Currently, if ``max_fee`` is not specified at any step it will default to ``None``,
    and will raise an exception when invoking a transaction.

    This behavior may change in the future. Always specify a ``max_fee`` yourself
    and do not rely on automatic values!

.. note::

    In future starknet versions invoke transactions with ``max_fee=0`` may be rejected.

Please note you will need to have enough Wei in your starknet account otherwise
transaction will be rejected.

Fee estimation
--------------

You can estimate required amount of fee that will need to be paid for transaction
using :meth:`Contract.PreparedFunctionCall.estimate_fee`

.. code-block:: python

    await contract.functions["put"].prepare(k, v, max_fee=5000).estimate_fee()

Automatic fee estimation
------------------------

For testing purposes it is possible to enable automatic fee estimation when making
a transaction. Starknet.py will then use ``estimate_fee()`` internally and use value
returned by it multiplied by ``1.1`` as a ``max_fee``. 

.. warning::

    Do not use automatic fee estimation in production code! It may lead to
    very high fees paid as the amount returned by ``estimate_fee()`` may be arbitrarily large.

.. code-block:: python

    await contract.functions["put"].invoke(k, v, auto_estimate=True)

Changes
-------

* `Client` methods ``get_transaction_status``, ``get_transaction`` and ``get_transaction_receipt`` no longer accept ``tx_id`` parameter.

* Starknet.py now supports named tuples from cairo-lang 0.8.0. see :ref:`Guide<Data transformation>`
