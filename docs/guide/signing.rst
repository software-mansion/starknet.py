Signing
=======

Using different signing methods
-------------------------------

By default, an :ref:`Account` uses the signing method of OpenZeppelin's account contract. If for any reason you want to use a different
signing algorithm, it is possible to create ``Account`` with custom
:ref:`Signer` implementation.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_custom_signer.py
    :language: python
    :dedent: 4


Signing off-chain messages
-------------------------------

:ref:`Account` lets you sign an off-chain message by using encoding standard proposed `here <https://github.com/argentlabs/argent-x/discussions/14>`_.
You can also **verify a message**, which is done by a call to ``is_valid_signature`` endpoint in the account's contract (e.g. `OpenZeppelin's account contract <https://github.com/starkware-libs/cairo-lang/blob/4e233516f52477ad158bc81a86ec2760471c1b65/src/starkware/starknet/third_party/open_zeppelin/Account.cairo#L115>`_).

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_sign_offchain_message.py
    :language: python
    :dedent: 4


Signing for fee estimation
--------------------------

:ref:`Account` allows signing transactions only for the purpose of fee estimation.
Transactions signed for fee estimation use a transaction version that prevents the execution
on StarkNet network. If a transaction like this was to be intercepted in transport, it could not
be executed without the user consent.

.. attention::

    Conventionally signed transactions can still be used to estimate fee. They however don't offer
    the extra security of signing specifically for the purpose of fee estimation.

    When manually estimating fee for transactions, always prefer estimation specific signing.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_sign_for_fee_estimate.py
    :language: python
    :dedent: 4