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
