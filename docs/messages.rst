StarkNet <> Ethereum Messaging
==============================

.. warning::
    StarkNet <> Ethereum Messaging module is deprecated. If you are using it,
    please contact us on our StarkNet discord channel: starknet-py.

.. _Messaging:

Module containing utilities to operate on StarkNet ->  Ethereum and Ethereum -> StarkNet messages

.. py:module:: starknet_py.net.l1.messages

.. autoclass:: MessageToEth
    :members: __init__, from_hash, from_content, from_tx_receipt, from_tx_hash, from_tx_hash_sync, count_queued_sync

.. autoclass:: MessageToEthContent

.. autoclass:: MessageToStarknet
    :members: __init__, from_hash, from_content, from_tx_receipt, from_tx_hash, from_tx_hash_sync, count_queued_sync

.. autoclass:: MessageToStarknetContent


