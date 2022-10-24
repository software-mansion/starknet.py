Guide
=====

Using existing contracts
------------------------

Although it is possible to use `Client` to interact with contracts, it requires translating python values into Cairo
values. Contract offers that and some other utilities.

Let's say we have a contract with this interface:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_using_existing_contracts.py
    :language: python
    :lines: 6-24


This is how we can interact with it:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_using_existing_contracts.py
    :language: python
    :lines: 34-40,44-49,57-66,70-74,78-82,86-101
    :dedent: 4


AccountClient details
---------------------

:ref:`Account Client` provides a simple way of executing transactions. To send one with few calls
just prepare calls through contract interface and send it with AccountClient.execute method.

Here is an example:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_account_client_details.py
    :language: python
    :lines: 8-13,17-21,26-56
    :dedent: 4



Using different signing methods
-------------------------------

By default, :ref:`Account Client` uses signing method of OpenZeppelin's account contract. If for any reason you want to use a different
signing algorithm, it is possible to create ``AccountClient`` with custom
:ref:`Signer` implementation.

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_custom_signer.py
    :language: python
    :lines: 11-41
    :dedent: 4


Signing off-chain messages
-------------------------------

:ref:`Account Client` lets you sign an off-chain message by using encoding standard proposed `here <https://github.com/argentlabs/argent-x/discussions/14>`_.
You can also **verify a message**, which is done by a call to ``is_valid_signature`` endpoint in the account's contract (e.g. `OpenZeppelin's account contract <https://github.com/starkware-libs/cairo-lang/blob/4e233516f52477ad158bc81a86ec2760471c1b65/src/starkware/starknet/third_party/open_zeppelin/Account.cairo#L115>`_).

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_sign_offchain_message.py
    :language: python
    :lines: 9-44,51-59,66-76
    :dedent: 4


Declaring contracts
-------------------

Since Cairo 0.10.0 Declare transactions can be signed and in the future, declaring without signing the transaction
(and without paying the fee) will be impossible. That is why :ref:`AccountClient` has
:meth:`sign_declare_transaction()` method.

Here's an example how to use it.

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_declaring_contracts.py
    :language: python
    :lines: 10-20
    :dedent: 4

.. note::

    Signing Declare transactions is possible only with Accounts having `__validate__` entrypoint (with `supported_tx_version = 1`).


Deploying new contracts
-----------------------

Here's how you can deploy new contracts:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_deploying_new_contracts.py
    :language: python
    :lines: 10-33,37-47,51-57,61-72
    :dedent: 4


Deploying new contracts with Universal Deployer Contract (UDC)
--------------------------------------------------------------

The best way of deploying contracts on Starknet is to use UDC. starknet.py assumes you use an implementation compatible
with `OpenZeppelin's UDC implementation <https://github.com/OpenZeppelin/cairo-contracts/blob/main/src/openzeppelin/utils/presets/UniversalDeployer.cairo>`_.

There is a class responsible for the deployment (:ref:`Deployer<Deployer>`).

Short code example how to use it:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_deploying_with_udc.py
    :language: python
    :lines: 18-19,29-35,40-54,60-93
    :dedent: 4


Fees
----

Starknet.py requires you to specify amount of Wei you
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


Handling client errors
-----------------------
You can use :class:`starknet_py.net.client_errors.ClientError` to catch errors from invalid requests:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_handling_client_errors.py
    :language: python
    :lines: 8-15,19-21
    :dedent: 4


Data transformation
-------------------

Starknet.py transforms python values to Cairo values and the other way around.

.. list-table:: Data transformation of ``parameter`` to Cairo values
   :widths: 25 25 25 25
   :header-rows: 1

   * - Expected Cairo type
     - Accepted python types
     - Example python values
     - Comment
   * - felt
     - int, string (at most 31 characters)
     - ``0``, ``1``, ``1213124124``, 'shortstring', ''
     - Provided int must be in range [0;P) - P being the Prime used in cairo-vm.
       Can also be provided a short 31 character string, which will get
       translated into felt with first letter as MSB of the felt
   * - tuple
     - any iterable of matching size
     - ``(1, 2, (9, 8))``, ``[1, 2, (9, 8)]``, ``(v for v in [1, 2, (9, 8)])``
     - Can nest other types apart from pointers
   * - named tuple
     - dict or NamedTuple
     - ``{"a": 1, "b": 2, "c" : (3, 4)}``, ``NamedTuple("name", [("a", int), ("b", int), ("c", tuple)])(1, 2, (3, 4))``
     -
   * - struct
     - dict with keys matching struct
     - ``{"key_1": 2, "key_2": (1, 2, 3), "key_3": {"other_struct_key": 13}}``
     - Can nest other types apart from pointers
   * - pointer to felt/felt arrays (requires additional ``parameter_len`` parameter)
     - any iterable containing ints
     - ``[1, 2, 3]``, ``[]``, ``(1, 2, 3)``
     - ``parameter_len`` is filled automatically from value
   * - pointer to struct/struct arrays (requires additional ``parameter_len`` parameter)
     - any iterable containing dicts
     - ``[{"key": 1}, {"key": 2}, {"key": 3}]``, ``[]``, ``({"key": 1}, {"key": 2}, {"key": 3})``
     - ``parameter_len`` is filled automatically from value
   * - uint256
     - int or dict with ``"low"`` and ``"high"`` keys and ints as values
     - ``0``, ``340282366920938463463374607431768211583``, ``{"low": 12, "high": 13}``
     -



.. list-table:: Data transformation of ``parameter`` from Cairo values
   :widths: 25 25
   :header-rows: 1

   * - Cairo type
     - Python type
   * - felt
     - int
   * - tuple
     - tuple
   * - named tuple
     - NamedTuple
   * - struct
     - dict with keys matching struct
   * - pointer to felt/felt arrays
     - list of ints
   * - pointer to struct/struct arrays
     - list of dicts
   * - unt256
     - int


Using CairoSerializer
---------------------

CairoSerializer can be used to transform any data (like a function call or an event) between cairo and python format. It requires an abi of the contract, types of values and data to be serialized.
Here is a usage example:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_using_cairo_serializer.py
    :language: python
    :lines: 9-39,44-49,54-97
    :dedent: 4


Working with shortstrings
-------------------------

To make working with short strings easier we provide some utility functions to translate the felt value received from the contract, into a short string value. A function which translates a string into a felt is also available, but the transformation is done automatically when calling the contract with shortstring in place of felt - they are interchangable.
You can read more about how cairo treats shortstrings in `the documentation <https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals>`_.

Conversion functions and references:

- :obj:`encode_shortstring <starknet_py.cairo.felt.encode_shortstring>`
- :obj:`decode_shortstring <starknet_py.cairo.felt.decode_shortstring>`


FullNodeClient usage
--------------------

Use a :ref:`FullNodeClient` to interact with services providing `starknet rpc interface <https://github.com/starkware-libs/starknet-specs/blob/606c21e06be92ea1543fd0134b7f98df622c2fbf/api/starknet_api_openrpc.json>`_
like `Pathfinder Full Node <https://github.com/eqlabs/pathfinder>`_ or starknet-devnet. StarkNet.py provides uniform interface for
both gateway and full node client - usage is exactly the same as gateway client minus some optional
parameters.

Using own full node allows for querying StarkNet with better performance.
Since gateway will be deprecated at some point in the future, having ``FullNodeClient`` with interface uniform with that of ``GatewayClient``
will allow for simple migration for StarkNet.py users.

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_full_node_client.py
    :language: python
    :lines: 12-15,24-25
    :dedent: 4


StarkNet <> Ethereum communication
----------------------------------

To retrieve the StarkNet -> Ethereum or Ethereum -> StarkNet message count, you need to provide some data that you used to create that message.
Then after creating the message's representation, you can query it's current count.

You can find out more about StarkNet <> Ethereum messaging here: https://starknet.io/documentation/l1-l2-messaging/

Full API description :ref:`here<Messaging>`.



Ethereum -> StarkNet messages
#############################

The message's count is an `int`, representing the number of unconsumed messages on L2 with that exact content.
Since the `nonce`'s value will always be unique for each message, this value is either 0 or 1
(0 meaning the message is consumed or not received yet, and 1 for unconsumed, queued message).

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_eth_sn_messages.py
    :language: python
    :lines: 12-42,49-49,63-75
    :dedent: 4


StarkNet -> Ethereum messages
#############################

As in previous section, you can provide L1 message content, and then fetch the queued message count.
The return value is an `int`, representing the number of unconsumed messages on L1 of that exact content.

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_sn_eth_messages.py
    :language: python
    :lines: 11-38,44-45,59-65,71-76
    :dedent: 4
