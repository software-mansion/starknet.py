Contract
========

.. py:module:: starknet_py.contract

.. autoclass:: Contract
    :members: from_address, __init__, functions, from_address_sync, compute_address, compute_contract_hash

.. autoclass:: ContractFunction
    :exclude-members: __init__, __new__
    :members: prepare, call, invoke, call_sync, invoke_sync, get_selector

.. autoclass:: PreparedFunctionCall
    :exclude-members: __init__, __new__
    :members: call, call_raw, invoke, call_sync, call_raw_sync, invoke_sync, estimate_fee, estimate_fee_sync

.. autoclass:: InvokeResult
    :exclude-members: __init__, __new__
    :members: wait_for_acceptance, wait_for_acceptance_sync, contract, invoke_transaction, hash, status, block_number
    :member-order: groupwise

.. autoclass:: DeployResult
    :exclude-members: __init__, __new__
    :members: wait_for_acceptance, wait_for_acceptance_sync, deployed_contract, hash, status, block_number
    :member-order: groupwise

.. autoclass:: DeclareResult
    :exclude-members: __init__, __new__
    :members: deploy, deploy_sync, wait_for_acceptance, wait_for_acceptance_sync, class_hash, compiled_contract, hash, status, block_number
    :member-order: groupwise
