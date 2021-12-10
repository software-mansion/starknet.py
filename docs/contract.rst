Contract
========

.. py:module:: starknet.contract

.. autoclass:: Contract
    :members: from_address, __init__, functions, deploy

.. autoclass:: ContractFunctionsRepository
    :exclude-members: __init__, __new__

.. autoclass:: ContractFunction
    :exclude-members: __init__, __new__
    :members: prepare, call, invoke

.. autoclass:: PreparedFunctionCall
    :exclude-members: __init__, __new__
    :members: call, call_raw, invoke

.. autoclass:: InvocationResult
    :exclude-members: __init__, __new__
    :members: wait_for_acceptance