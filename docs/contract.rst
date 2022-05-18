Contract
========

.. py:module:: starknet_py.contract

.. autoclass:: Contract
    :members: from_address, __init__, functions, deploy, from_address_sync, deploy_sync, compute_address, compute_contract_hash, ProxyConfig

.. autoclass:: ContractFunction
    :exclude-members: __init__, __new__
    :members: prepare, call, invoke, call_sync, invoke_sync, get_selector

.. autoclass:: PreparedFunctionCall
    :exclude-members: __init__, __new__
    :members: call, call_raw, invoke, call_sync, call_raw_sync, invoke_sync, hash, estimate_fee, estimate_fee_sync

.. autoclass:: InvokeResult
    :exclude-members: __init__, __new__
    :members: wait_for_acceptance, wait_for_acceptance_sync

.. autoclass:: DeployResult
    :exclude-members: __init__, __new__
    :members: wait_for_acceptance, wait_for_acceptance_sync
