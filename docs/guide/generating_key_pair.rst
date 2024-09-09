Generating a Key pair
=====================

Key pair
--------

The Key pair is a pair of private and public keys. The private key is used to sign transactions, and the public key is used to verify the signature.
In the starknet.py you need to use the :class:`~starknet_py.net.signer.key_pair.KeyPair` class to be able to create an :class:`~starknet_py.net.account.account.Account` and :class:`~starknet_py.net.signer.stark_curve_signer.StarkCurveSigner` object.

Generating random key pair
--------------------------

Method :meth:`~starknet_py.net.signer.stark_curve_signer.KeyPair.generate` allows to generate cryptographically strong pseudo-random numbers
suitable for managing secrets such as account authentication, tokens, and similar.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_key_pair.py
    :language: python
    :dedent: 4
    :start-after: docs-generate: start
    :end-before: docs-generate: end


Creating key pair from private Key
----------------------------------

To create a key pair from a private key, use the :meth:`~starknet_py.net.signer.stark_curve_signer.KeyPair.from_private_key` method.


.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_key_pair.py
    :language: python
    :dedent: 4
    :start-after: docs-from-private-key: start
    :end-before: docs-from-private-key: end

Reading key pair from keystore file
-----------------------------------

Using :meth:`~starknet_py.net.signer.stark_curve_signer.KeyPair.from_keystore` method there is possibility to import a key pair from a keystore file.
The keystore file should follow the `Ethereum keystore <https://github.com/ethereum/wiki/wiki/Web3-Secret-Storage-Definition#scrypt>`_ format.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_key_pair.py
    :language: python
    :dedent: 4
    :start-after: docs-from-keystore: start
    :end-before: docs-from-keystore: end

