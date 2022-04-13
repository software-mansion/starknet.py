Client
======
.. py:module:: starknet_py.net
.. py:class:: Client

.. automethod:: Client.__init__
.. automethod:: Client.get_contract_addresses
.. automethod:: Client.get_contract_addresses_sync
.. automethod:: Client.call_contract
.. automethod:: Client.call_contract_sync

We recommend using :obj:`ContractFunction's call <starknet_py.contract.ContractFunction.call>` instead.

.. automethod:: Client.get_block
.. automethod:: Client.get_block_sync

Example response:

.. code-block:: json

    {
        "block_hash": "0x39a53f921b51af73e95ecf13ffe1542da069f680531e8a36b2f6b656e45a162",
        "block_number": 0,
        "parent_block_hash": "0x0",
        "state_root": "079354de0075c5c1f2a6af40c7dd70a92dc93c68b54ecc327b61c8426fea177c",
        "status": "PENDING",
        "timestamp": 105,
        "transaction_receipts": [
            {
                "block_hash": "0x39a53f921b51af73e95ecf13ffe1542da069f680531e8a36b2f6b656e45a162",
                "block_number": 0,
                "execution_resources": {
                    "builtin_instance_counter": {},
                    "n_memory_holes": 0,
                    "n_steps": 0
                },
                "l2_to_l1_messages": [],
                "status": "PENDING",
                "transaction_hash": "0x50f392748f303a37f0a9053b7295d51231bee3e0a9dbf42bcb1c8392e4d8503",
                "transaction_index": 0
            },
            {
                "block_hash": "0x39a53f921b51af73e95ecf13ffe1542da069f680531e8a36b2f6b656e45a162",
                "block_number": 0,
                "execution_resources": {
                    "builtin_instance_counter": {
                        "bitwise_builtin": 0,
                        "ec_op_builtin": 0,
                        "ecdsa_builtin": 0,
                        "output_builtin": 0,
                        "pedersen_builtin": 0,
                        "range_check_builtin": 0
                    },
                    "n_memory_holes": 0,
                    "n_steps": 65
                },
                "l2_to_l1_messages": [],
                "status": "PENDING",
                "transaction_hash": "0x1ba395964b6d4308b14a78a8f6f59dbc0c753ad966e5d3e1e3118ca29e10841",
                "transaction_index": 1
            }
        ],
        "transactions": [
            {
                "constructor_calldata": [],
                "contract_address": "0x05a4d278dceae5ff055796f1f59a646f72628730b7d72acb5483062cb1ce82dd",
                "contract_address_salt": "0x0",
                "transaction_hash": "0x602e4b4e9e046d2692af3702fe013fef996df040af335223e7526c9c4fe6fb",
                "type": "DEPLOY"
            },
            {
                "calldata": [
                    "1234"
                ],
                "contract_address": "0x05a4d278dceae5ff055796f1f59a646f72628730b7d72acb5483062cb1ce82dd",
                "entry_point_selector": "0x362398bec32bc0ebb411203221a35a0301193a96f317ebe5e40be9f60d15320",
                "entry_point_type": "EXTERNAL",
                "signature": [],
                "transaction_hash": "0x142ca10924ad813764aa8f7ac7c298721708bf531d12d6e5fc4bda3cf9c7904",
                "type": "INVOKE_FUNCTION"
            }
        ]
    }


.. automethod:: Client.get_code
.. automethod:: Client.get_code_sync

The output should look like:

.. code-block:: json

    {
        "abi": [
            {
                "inputs": [
                    {
                        "name": "amount",
                        "type": "felt"
                    }
                ],
                "name": "increase_balance",
                "outputs": [],
                "type": "function"
            },
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x208b7fff7fff7ffe"
        ]
    }

.. automethod:: Client.get_storage_at
.. automethod:: Client.get_storage_at_sync
.. automethod:: Client.get_transaction_status
.. automethod:: Client.get_transaction_status_sync

The result should look like this:

.. code-block:: json

    {
        "block_hash": "0x0",
        "tx_status": "PENDING"
    }

The possible statuses are:

- **NOT_RECEIVED**: The transaction has not been received yet (i.e., not written to storage).
- **RECEIVED**: The transaction was received by the operator.
- **PENDING**: The transaction passed the validation and is waiting to be sent on-chain.
- **REJECTED**: The transaction failed validation and thus was skipped.
- **ACCEPTED_ON_L1**: The transaction was accepted on layer 1.
- **ACCEPTED_ON_L2**: The transaction was accepted on layer 2.

.. automethod:: Client.get_transaction
.. automethod:: Client.get_transaction_sync

Example response:

.. code-block:: json

    {
        "block_hash": "0x0",
        "block_number": 0,
        "status": "PENDING",
        "transaction": {
            "calldata": [
                "1234"
            ],
            "contract_address": "0x039564c4f6d9f45a963a6dc8cf32737f0d51a08e446304626173fd838bd70e1c",
            "entry_point_selector": "0x362398bec32bc0ebb411203221a35a0301193a96f317ebe5e40be9f60d15320",
            "entry_point_type": "EXTERNAL",
            "signature": [],
            "transaction_hash": "0x69d743891f69d758928e163eff1e3d7256752f549f134974d4aa8d26d5d7da8",
            "type": "INVOKE_FUNCTION"
        },
        "transaction_index": 1
    }

The result contains:

- `transaction_hash` – The hash of the transaction, out of all sent transactions.
- `status` – The status of the transaction. For a detailed list of supported transaction statuses, refer to the tx_status usage example.
- `transaction` – The transaction data.

It may also include each of the following optional fields (according to the transaction’s status):

- `block_hash` – The hash of the block containing the transaction.
- `block_number` – The sequence number of the block containing the transaction.
- `transaction_index` – The index of the transaction within the block containing it.
- `transaction_failure_reason` – The reason for the transaction failure.



.. automethod:: Client.get_transaction_receipt
.. automethod:: Client.get_transaction_receipt_sync

Example response:

.. code-block:: json

    {
        "block_hash": "0x0",
        "block_number": 0,
        "execution_resources": {
            "builtin_instance_counter": {
                "bitwise_builtin": 0,
                "ec_op_builtin": 0,
                "ecdsa_builtin": 0,
                "output_builtin": 0,
                "pedersen_builtin": 2,
                "range_check_builtin": 8
            },
            "n_memory_holes": 22,
            "n_steps": 168
        },
        "l2_to_l1_messages": [
            {
                "from_address": "0x7dacca7a41e893630664a61f4d8ec05550ca1a212849c62417cb3ecf4bad863",
                "payload": [
                    "0",
                    "12345678",
                    "1000"
                ],
                "to_address": "0x9E4c14403d7d9A8A782044E86a93CAE09D7B2ac9"
            }
        ],
        "status": "PENDING",
        "transaction_hash": "0x7797c6673a1a0aeebbcb1c726702e263e5138123124ddef7edd85cd925b11ec",
        "transaction_index": 2
    }

The result contains (in addition to get_transaction fields):

- ``l2_to_l1_messages`` – Messages sent from L2 to L1.
- ``l1_to_l2_consumed_message`` – The consumed message, in case the transaction was sent from L1.
- ``execution_resources`` – Resources consumed by the transaction execution.

.. automethod:: Client.wait_for_tx
.. automethod:: Client.wait_for_tx_sync

.. automethod:: Client.add_transaction
.. automethod:: Client.add_transaction_sync

We recommend using :obj:`ContractFunction's invoke <starknet_py.contract.ContractFunction.invoke>` or :obj:`Contract's deploy <starknet_py.contract.Contract.deploy>` instead

.. automethod:: Client.estimate_fee
.. automethod:: Client.estimate_fee_sync
