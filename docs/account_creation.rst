Account creation
================

Creating an account on StarkNet
-------------------------------

An account is needed to start interacting with StarkNet.
If you don't have one there are a few ways of creating one programmatically:

 - using DeployAccount transaction
 - deploy through Cairo syscall (another account is needed)

The first approach is recommended since it doesn't rely on third-party contracts.

Deploying an account with DeployAccount transaction requires the following:

 - class_hash of the account contract
 - generating a private key and deployment salt
 - computing an address based on the account's secrets
 - prefunding an address with the fee tokens (e.g. using the bridge)
 - creating and signing a DeployAccount transaction with generated secrets
 - sending the transaction to StarkNet

Here is step by step example:

.. literalinclude:: ../starknet_py/tests/e2e/docs/setup/test_deploy_prefunded_account.py
    :language: python
    :lines: 13-39,46-65
    :dedent: 4