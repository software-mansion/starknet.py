Account
=======

.. py:module:: starknet_py.net.account.base_account

.. autoclass:: BaseAccount
    :members:

The default implementation, supplied with StarkNet.py is Account

.. py:module:: starknet_py.net.account.account

.. autoclass:: Account
    :members:

Result of the Account deployment

.. py:module:: starknet_py.net.account.account_deployment_result

.. autoclass:: AccountDeploymentResult
    :exclude-members: __new__, __init__
    :members: wait_for_acceptance, wait_for_acceptance_sync, account, hash, status, block_number
    :member-order: groupwise
