Signer
======

--------------------
BaseSigner interface
--------------------

.. py:module:: starknet_py.net.signer

.. autoclass:: BaseSigner
    :members:
    :undoc-members:
    :member-order: groupwise

---------------------------------
BaseSigner default implementation
---------------------------------

By default, StarkNet.py uses ``StarkCurveSigner`` which works with OpenZeppelin's account contract.

.. py:module:: starknet_py.net.signer.stark_curve_signer

.. autoclass:: StarkCurveSigner
    :members:
    :undoc-members:
    :member-order: groupwise

-------
KeyPair
-------

.. autoclass:: KeyPair
    :members:
    :undoc-members:
    :member-order: groupwise

