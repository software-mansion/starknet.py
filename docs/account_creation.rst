Account creation
================


An account is needed to start interacting with StarkNet.
If you don't have one there are a few ways of creating one programmatically:

 - using DeployAccount transaction
 - deploy through Cairo syscall (another account is needed)
 - using :ref:`Universal Deployer Contract <UDC paragraph>` (another account is needed)

The first approach is recommended since it doesn't rely on third-party contracts.
The concept behind the DeployAccount transaction is based on prefunding a generated address with tokens
and then creating the transaction which will charge the fee from the address.

Deploying an account with DeployAccount transaction requires the following:

 - class_hash of the account contract
 - generating a private key and deployment salt
 - computing an address based on the account's secrets
 - prefunding an address with the fee tokens (e.g. using the token bridge)
 - creating and signing a DeployAccount transaction with generated secrets
 - sending the transaction to StarkNet

Here is step by step example:

.. codesnippet:: ../starknet_py/tests/e2e/docs/account_creation/test_deploy_prefunded_account.py
    :language: python
    :dedent: 4

.. hint::

    If you are experiencing transaction failures with ``FEE_TRANSFER_FAILURE``
    make sure that the address you are trying to deploy is prefunded with enough
    tokens, and verify that ``max_fee`` argument
    in :meth:`~starknet_py.net.account.account.Account.sign_deploy_account_transaction` is set
    to a high enough value.
