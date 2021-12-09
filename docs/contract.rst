Contract
========

.. py:module:: starknet.contract

.. autoclass:: Contract
    :members: from_address, __init__, functions

.. autoclass:: ContractFunctionsRepository
    :exclude-members: __init__, __new__

.. autoclass:: ContractFunction
    :exclude-members: __init__, __new__
    :members: call, invoke

.. autoclass:: InvocationResult
    :exclude-members: __init__, __new__
    :members: wait_for_acceptance