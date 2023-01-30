Account
=======

---------------------
BaseAccount interface
---------------------

.. py:module:: starknet_py.net.account.base_account

.. autoclass:: BaseAccount
    :members:
    :undoc-members:
    :member-order: groupwise

----------------------------------
BaseAccount default implementation
----------------------------------

.. py:module:: starknet_py.net.account.account

.. autoclass-with-examples:: Account
    :members:
    :undoc-members:
    :member-order: groupwise

------------------
Account deployment
------------------

Result of the Account deployment.

.. py:module:: starknet_py.net.account.account_deployment_result

.. autoclass:: AccountDeploymentResult
    :exclude-members: __new__, __init__
    :members: wait_for_acceptance, wait_for_acceptance_sync, account, hash, status, block_number
    :member-order: groupwise
