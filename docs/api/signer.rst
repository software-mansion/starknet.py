Signer
======

--------------------
BaseSigner interface
--------------------

.. py:module:: starknet_py.net.signer

.. autoclass:: BaseSigner
    :members:
    :member-order: groupwise

---------------------------------
BaseSigner default implementation
---------------------------------

By default, starknet.py uses ``StarkCurveSigner`` which works with OpenZeppelin's account contract.

.. py:module:: starknet_py.net.signer.stark_curve_signer

.. autoclass:: StarkCurveSigner
    :members:
    :member-order: groupwise

-------
KeyPair
-------

.. autoclass:: KeyPair
    :members:
    :undoc-members:
    :member-order: groupwise

------------
LedgerSigner
------------

To use LedgerSigner, you need to install starknetpy with `ledger` extra like this:

.. code-block:: bash

    poetry add starknet_py[ledger]

.. py:module:: starknet_py.net.signer.ledger_signer

.. autoclass:: LedgerSigner
    :members:
    :member-order: groupwise

-----------------
LedgerSigningMode
-----------------

.. autoclass:: LedgerSigningMode
    :members:
    :member-order: groupwise

------------
EthSigner
------------

Signer compatible with the Ethereum signature.

.. py:module:: starknet_py.net.signer.eth_signer

.. autoclass:: EthSigner
    :members:
    :member-order: groupwise
