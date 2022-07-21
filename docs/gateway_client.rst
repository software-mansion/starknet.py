GatewayClient
=============
.. py:module:: starknet_py.net.gateway_client
.. py:class:: GatewayClient

.. automethod:: GatewayClient.__init__
.. automethod:: GatewayClient.get_contract_addresses
.. automethod:: GatewayClient.get_contract_addresses_sync
.. automethod:: GatewayClient.call_contract
.. automethod:: GatewayClient.call_contract_sync

We recommend using :obj:`ContractFunction's call <starknet_py.contract.ContractFunction.call>` instead.

.. automethod:: GatewayClient.get_block
.. automethod:: GatewayClient.get_block_sync
.. automethod:: GatewayClient.get_block_traces
.. automethod:: GatewayClient.get_block_traces_sync

.. automethod:: GatewayClient.get_code
.. automethod:: GatewayClient.get_code_sync

.. automethod:: GatewayClient.get_storage_at
.. automethod:: GatewayClient.get_storage_at_sync
.. automethod:: GatewayClient.get_transaction_status
.. automethod:: GatewayClient.get_transaction_status_sync


The possible statuses are:

- **NOT_RECEIVED**: The transaction has not been received yet (i.e., not written to storage).
- **RECEIVED**: The transaction was received by the operator.
- **PENDING**: The transaction passed the validation and is waiting to be sent on-chain.
- **REJECTED**: The transaction failed validation and thus was skipped.
- **ACCEPTED_ON_L1**: The transaction was accepted on layer 1.
- **ACCEPTED_ON_L2**: The transaction was accepted on layer 2.

.. automethod:: GatewayClient.get_transaction
.. automethod:: GatewayClient.get_transaction_sync


The result contains:

- `transaction_hash` – The hash of the transaction, out of all sent transactions.
- `status` – The status of the transaction. For a detailed list of supported transaction statuses, refer to the tx_status usage example.
- `transaction` – The transaction data.

It may also include each of the following optional fields (according to the transaction’s status):

- `block_hash` – The hash of the block containing the transaction.
- `block_number` – The sequence number of the block containing the transaction.
- `transaction_index` – The index of the transaction within the block containing it.
- `transaction_failure_reason` – The reason for the transaction failure.



.. automethod:: GatewayClient.get_transaction_receipt
.. automethod:: GatewayClient.get_transaction_receipt_sync

The result contains (in addition to get_transaction fields):

- ``l2_to_l1_messages`` – Messages sent from L2 to L1.
- ``l1_to_l2_consumed_message`` – The consumed message, in case the transaction was sent from L1.
- ``execution_resources`` – Resources consumed by the transaction execution.

.. automethod:: GatewayClient.wait_for_tx
.. automethod:: GatewayClient.wait_for_tx_sync

.. automethod:: GatewayClient.send_transaction
.. automethod:: GatewayClient.send_transaction_sync

We recommend using :obj:`ContractFunction's invoke <starknet_py.contract.ContractFunction.invoke>` or :obj:`Contract's deploy <starknet_py.contract.Contract.deploy>` instead

.. automethod:: GatewayClient.estimate_fee
.. automethod:: GatewayClient.estimate_fee_sync
