Account creation
================

Creating an account on StarkNet
-------------------------------

An account is needed to start interacting with StarkNet.
If you don't have one there are a few ways of creating one programmatically:

 - using DeployAccount transaction
 - deploy through Cairo syscall (another account is needed)

.. note::

    In the future users will be able to use
    `Universal Deployer Contract <https://community.starknet.io/t/universal-deployer-contract-proposal/1864>`_
    to deploy any contract, including an Account.

The first approach is recommended since it doesn't rely on third-party contracts.
The concept behind the DeployAccount transaction is based on prefunding a generated address with tokens
and then creating the transaction which will charge the fee from the address.

Deploying an account with DeployAccount transaction requires the following:

 - class_hash of the account contract
 - generating a private key and deployment salt
 - computing an address based on the account's secrets
 - prefunding an address with the fee tokens (e.g. using the bridge)
 - creating and signing a DeployAccount transaction with generated secrets
 - sending the transaction to StarkNet

Here is step by step example:

.. literalinclude:: ../starknet_py/tests/e2e/docs/account_creation/test_deploy_prefunded_account.py
    :language: python
    :lines: 16-22,28-40,47-68
    :dedent: 4