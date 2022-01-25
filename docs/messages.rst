L1 <> L2 Messaging
==================

.. _Messaging:

Module containing utilities to operate on L1 -> L2 and L2 -> L1 messages

.. py:module:: starknet_py.net.l1.messages

.. autoclass:: L2ToL1Message
    :members: __init__, from_hash, from_content, from_tx_receipt, from_tx_hash, from_tx_hash_sync, count_queued, count_queued_sync

.. autoclass:: L2ToL1MessageContent

.. autoclass:: L1ToL2Message
    :members: __init__, from_hash, from_content, from_tx_receipt, from_tx_hash, from_tx_hash_sync, count_queued, count_queued_sync

.. autoclass:: L1ToL2MessageContent


