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

The simplest way of declaring and deploying contracts on the Starknet is to use the :ref:`Contract` class.
Under the hood, this flow sends :meth:`Declare` transaction and then sends :meth:`InvokeFunction`
through Universal Deployment Contract (UDC) to deploy a contract.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_simple_declare_and_deploy.py
    :language: python
    :dedent: 4

Simple deploy
-------------

If you already know the class hash of an already declared contract you want to deploy just use the :meth:`Contract.deploy_contract`.
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


Cairo1 contracts
----------------

Declaring Cairo1 contracts
##########################

| Starknet 0.11 introduced the ability to declare contracts written in Cairo1!

To declare a new contract, Declare v2 transaction has to be sent.
You can see the structure of the new Declare transaction `here <https://docs.starknet.io/documentation/starknet_versions/upcoming_versions/#declare_v2>`_.

The main differences in the structure of the transaction from its previous version are:
 - ``contract_class`` field is a ``SierraContractClass``
 - ``compiled_class_hash`` is the hash obtained from ``CasmClass`` using ``starknet_py.hash.compute_casm_class_hash``

The ``SierraContractClass`` in its ``json`` format can be obtained through the compiler in `Cairo1 repo <https://github.com/starkware-libs/cairo>`_.
The command used to get the class is ``starknet-compile``.

To get ``compiled_class_hash``, ``CasmClass`` will be needed. It can be obtained in a similar way to ``SierraContractClass``.
Simply pluck the ``json`` result of ``starknet-compile`` into ``starknet-sierra-compile`` from the Cairo1 repository.

.. note::

    The compilation to Cairo Assembly should use the ``--add-pythonic-hints`` flag.


Here's an example how to declare a Cairo1 contract.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_cairo1_contract.py
    :language: python
    :dedent: 4

.. note::

    This is currently the only supported method of declaring a Cairo1 contract to Starknet.
    The support for declaring through :ref:`Contract` interface is planned for a future release.


Deploying Cairo1 contracts
##########################

After declaring a Cairo1 contract, it can be deployed using UDC.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_cairo1_contract.py
    :language: python
    :dedent: 4
    :start-after: docs-deploy: start
    :end-before: docs-deploy: end

.. note::

    Currently only :meth:`~starknet_py.net.udc_deployer.deployer.Deployer.create_contract_deployment_raw` is supported.
    :meth:`~starknet_py.net.udc_deployer.deployer.Deployer.create_contract_deployment` will not work.

