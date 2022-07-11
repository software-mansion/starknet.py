FullNodeClient
==============
.. py:module:: starknet_py.net.full_node_client
.. py:class:: FullNodeClient

.. automethod:: FullNodeClient.__init__
.. automethod:: FullNodeClient.call_contract
.. automethod:: FullNodeClient.call_contract_sync

We recommend using :obj:`ContractFunction's call <starknet_py.contract.ContractFunction.call>` instead.

.. automethod:: FullNodeClient.get_block
.. automethod:: FullNodeClient.get_block_sync

.. automethod:: FullNodeClient.get_state_update
.. automethod:: FullNodeClient.get_state_update_sync

.. automethod:: FullNodeClient.get_storage_at
.. automethod:: FullNodeClient.get_storage_at_sync

.. automethod:: FullNodeClient.get_transaction
.. automethod:: FullNodeClient.get_transaction_sync

.. automethod:: FullNodeClient.get_transaction_by_block_hash
.. automethod:: FullNodeClient.get_transaction_by_block_hash_sync

.. automethod:: FullNodeClient.get_transaction_by_block_number
.. automethod:: FullNodeClient.get_transaction_by_block_number_sync

.. automethod:: FullNodeClient.get_transaction_receipt
.. automethod:: FullNodeClient.get_transaction_receipt_sync

.. automethod:: FullNodeClient.get_class_hash_at
.. automethod:: FullNodeClient.get_class_hash_at_sync

.. automethod:: FullNodeClient.get_class_by_hash
.. automethod:: FullNodeClient.get_class_by_hash_sync

.. automethod:: FullNodeClient.wait_for_tx
.. automethod:: FullNodeClient.wait_for_tx_sync

We recommend using :obj:`ContractFunction's invoke <starknet_py.contract.ContractFunction.invoke>` or :obj:`Contract's deploy <starknet_py.contract.Contract.deploy>` instead

.. automethod:: FullNodeClient.estimate_fee
.. automethod:: FullNodeClient.estimate_fee_sync
