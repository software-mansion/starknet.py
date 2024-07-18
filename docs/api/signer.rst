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

.. py:module:: starknet_py.net.signer.key_pair

.. autoclass:: KeyPair
    :members:
    :undoc-members:
    :member-order: groupwise

------------
LedgerSigner
------------

.. py:module:: starknet_py.net.signer.ledger_signer

.. autoclass:: LedgerSigner
    :members:
    :member-order: groupwise
