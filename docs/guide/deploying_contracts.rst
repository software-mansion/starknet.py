Deploying contracts
===================

Declaring contracts
-------------------

A declare transaction can be issued in version 2 or 3. Contracts written in Cairo 0 cannot be declared while those written in Cairo 1 or higher should be declared with versions 2 or 3.
To sign a declare transaction, you should utilize the :meth:`~starknet_py.net.account.account.Account.sign_declare_v2` or :meth:`~starknet_py.net.account.account.Account.sign_declare_v3` method, respectively.

Here's an example how to use it.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_declaring_contracts.py
    :language: python
    :dedent: 4


Simple deploy
-------------

If you know the class hash of an already declared contract you want to deploy just use the :meth:`~starknet_py.contract.Contract.deploy_contract_v1` or :meth:`~starknet_py.contract.Contract.deploy_contract_v3`.
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

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_deploying_in_multicall.py
    :language: python
    :dedent: 4


Cairo1 contracts
----------------

Declaring Cairo1 contracts
##########################

To declare a contract in Cairo version 1 or higher, Declare V2 or Declare V3 transaction has to be sent.
You can see the structure of these transactions `here <https://docs.starknet.io/documentation/architecture_and_concepts/Network_Architecture/transactions/#declare-transaction>`_.

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


Deploying Cairo1 contracts
##########################

After declaring a Cairo1 contract, it can be deployed using UDC.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_cairo1_contract.py
    :language: python
    :dedent: 4
    :start-after: docs-deploy: start
    :end-before: docs-deploy: end


Simple declare and deploy Cairo1 contract example
#################################################

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_simple_declare_and_deploy_cairo1.py
    :language: python
    :dedent: 4
    :start-after: docs: start
    :end-before: docs: end


Simple deploy Cairo1 contract example
#####################################

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_simple_deploy_cairo1.py
    :language: python
    :dedent: 4
    :start-after: docs: start
    :end-before: docs: end
