Account setup
=============

Creating an account on StarkNet
-------------------------------

An account is needed to start interacting with StarkNet. There are a few ways of creating one:

 - using DeployAccount transaction
 - deploy through Cairo syscall (another account is needed)

The first approach is recommended since it doesn't rely on third-party contracts.

Deploying an account with DeployAccount transaction requires the following:

 - class_hash of the account contract
 - generating an account's secrets
 - computing an address based on the account's secrets
 - pre-founding an address with the fee tokens (e.g. using the bridge)
 - creating and signing a DeployAccount transaction with generated secrets
 - sending the transaction to StarkNet

Here is step by step example:

.. literalinclude:: ../starknet_py/tests/e2e/docs/setup/test_deploy_prefunded_account.py
    :language: python
    :lines: 13-39,46-65
    :dedent: 4