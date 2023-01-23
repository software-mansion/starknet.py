Deploying contracts
===================

Declaring contracts
-------------------

Since Cairo 0.10.0 Declare transactions can be signed and in the future, declaring without signing the transaction
(and without paying the fee) will be impossible. That is why :ref:`Account` has
:meth:`sign_declare_transaction()` method.

Here's an example how to use it.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_declaring_contracts.py
    :language: python
    :dedent: 4

.. note::

    Signing Declare transactions is possible only with Accounts having `__validate__` entrypoint (with `supported_tx_version = 1`).



Simple declare and deploy
-------------------------

The simplest way of declaring and deploying contracts on the StarkNet is to use the :ref:`Contract` class.
Under the hood, this flow sends :meth:`Declare` transaction and then sends :meth:`InvokeFunction`
through Universal Deployment Contract (UDC) to deploy a contract.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_simple_declare_and_deploy.py
    :language: python
    :dedent: 4

Simple deploy
-------------

If you already know a class_hash of a contract you want to deploy just use the :meth:`Contract.deploy_contract`.
It will deploy the contract using funds from your account. Deployment is handled by UDC.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_simple_deploy.py
    :language: python
    :dedent: 4

.. _UDC paragraph:

Using Universal Deployer Contract (UDC)
---------------------------------------

Using UDC is a way of deploying contracts if you already have an account. starknet.py assumes that UDC uses an implementation compatible
with `OpenZeppelin's UDC implementation <https://github.com/OpenZeppelin/cairo-contracts/blob/main/src/openzeppelin/utils/presets/UniversalDeployer.cairo>`_.

There is a class responsible for the deployment (:ref:`Deployer<Deployer>`).

Short code example of how to use it:

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_deploying_with_udc.py
    :language: python
    :dedent: 4

Deploying and using deployed contract in the same transaction
#############################################################

:ref:`Deployer` is designed to work with multicalls too. It allows to deploy a contract
and call its methods in the same multicall, ensuring atomicity of all operations combined.
Isn't it brilliant? Check out the code!

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_deploying_in_multicall.py
    :language: python
    :dedent: 4
