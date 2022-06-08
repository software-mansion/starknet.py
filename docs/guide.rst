Guide
=====

Using existing contracts
------------------------

Although it is possible to use :ref:`Client` to interact with contracts, it requires translating python values into Cairo
values. Contract offers that and some other utilities.

Let's say we have a contract with this interface:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_using_existing_contracts.py
    :language: python
    :lines: 7-25


This is how we can interact with it:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_using_existing_contracts.py
    :language: python
    :lines: 37-45,61-93
    :dedent: 4

Signing a single transaction
----------------------------
You can use :obj:`ContractFunction's call <starknet_py.contract.ContractFunction.prepare>` to get calldata's parts and generate a signature from them. Here's a contract inspired by `Starknet's docs <https://www.cairo-lang.org/docs/hello_starknet/user_auth.html>`_:

.. code-block:: text

    %lang starknet

    %builtins pedersen range_check ecdsa

    from starkware.cairo.common.uint256 import Uint256
    from starkware.cairo.common.cairo_builtins import (HashBuiltin, SignatureBuiltin)
    from starkware.cairo.common.hash import hash2
    from starkware.cairo.common.signature import (verify_ecdsa_signature)
    from starkware.starknet.common.syscalls import get_tx_signature

    @storage_var
    func balance(user) -> (res: Uint256):
    end

    @external
    func set_balance{
            syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
            range_check_ptr, ecdsa_ptr : SignatureBuiltin*}(
            user : felt, amount : Uint256):
        let (sig_len : felt, sig : felt*) = get_tx_signature()

        # Verify the signature length.
        assert sig_len = 2

        let (hash) = hash2{hash_ptr=pedersen_ptr}(amount.low, 0)
        let (amount_hash) = hash2{hash_ptr=pedersen_ptr}(amount.high, hash)

        # Verify the user's signature.
        verify_ecdsa_signature(
            message=amount_hash,
            public_key=user,
            signature_r=sig[0],
            signature_s=sig[1])

        balance.write(user, amount)
        return ()
    end

    @external
    func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(user : felt) -> (balance: Uint256):
        let (value) = balance.read(user=user)
        return (value)
    end

Here's how you could sign an invocation:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_signing_single_transaction.py
    :language: python
    :lines: 14-28,41-54
    :dedent: 4


Deploying new contracts
-----------------------

Here's how you can deploy new contracts:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_deploying_new_contracts.py
    :language: python
    :lines: 12-38,42-71
    :dedent: 4


Handling client errors
-----------------------
You can use ``starknet.net.client.BadRequest`` to catch errors from invalid requests:

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_handling_client_errors.py
    :language: python
    :lines: 9-15,19-21
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


Working with shortstrings
-------------------------

To make working with short strings easier we provide some utility functions to translate the felt value received from the contract, into a short string value. A function which translates a string into a felt is also available, but the transformation is done automatically when calling the contract with shortstring in place of felt - they are interchangable.
You can read more about how cairo treats shortstrings in `the documentation <https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals>`_.

Conversion functions and references:

- :obj:`encode_shortstring <starknet_py.cairo.felt.encode_shortstring>`
- :obj:`decode_shortstring <starknet_py.cairo.felt.decode_shortstring>`



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
    :lines: 12-42,49,63-75
    :dedent: 4


StarkNet -> Ethereum messages
#############################

As in previous section, you can provide L1 message content, and then fetch the queued message count.
The return value is an `int`, representing the number of unconsumed messages on L1 of that exact content.

.. literalinclude:: ../starknet_py/tests/e2e/docs/guide/test_sn_eth_messages.py
    :language: python
    :lines: 12-39,45-46,60-66,72-77
    :dedent: 4
