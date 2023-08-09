Migration guide
===============

**********************
0.18.0 Migration guide
**********************

This version of starknet.py brings support Starknet 0.12.1 and `RPC v0.4.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.4.0>`!


1. :class:`TransactionReceipt` dataclass properties have been changed (more details in RPC specification linked above).

0.18.0 Deprecations
-------------------

.. currentmodule:: starknet_py.net.client_models

1. ``status`` field in :class:`TransactionReceipt` returned by :meth:`FullNodeClient.get_transaction_receipt` has been deprecated.


0.18.0 Minor changes
--------------------

.. currentmodule:: starknet_py.net.full_node_client

1. :meth:`FullNodeClient.get_transaction_receipt` now returns two additional fields: ``acceptance_status`` and ``finality_status``.

.. currentmodule:: starknet_py.net.client_models

2. Added two fields to :class:`TransactionReceipt` - ``revert_error`` (Gateway) and ``revert_reason`` (FullNode).
3. ``hash`` property in :class:`Transaction` is now optional.
4. Added missing field ``contract_address_salt`` to :class:`DeployTransaction`.

.. currentmodule:: starknet_py.net.client

5. Lowered ``check_interval`` parameter default value in :meth:``Client.wait_for_tx`` from 5 seconds to 2.

.. currentmodule:: starknet_py.net.client_models

6. Added fields to dataclasses that previously were missing (e.g. ``contract_address_salt`` in :class:`DeployTransaction`).

.. currentmodule:; starknet_py.cairo.felt

7. :func:`decode_shortstring` now is returned without ``\x00`` in front of the decoded string.


0.18.0 Bugfixes
---------------

1. Fixed invalid type in :class:`BlockStateUpdate` from ``StateDiff`` to ``Union[StateDiff, GatewayStateDiff]``
2. Fixed ``Contract not found`` error in ``AbiResolver``


|

.. raw:: html

  <hr>

|

**********************
0.17.0 Migration guide
**********************

With Starknet 0.12.0, the ``PENDING`` transaction status has been removed.


:class:`Contract` now supports contracts written in **Cairo1** in both old and new syntax.

To create an instance of such contract, a keyword parameter ``cairo_version=1`` in the Contract constructor is required.


.. note::
    Please note that while using the interface with `Cairo1` contracts, it is possible for problems to occur due to some of the types being not yet implemented in the parser.

    In such case, please open an issue at our `GitHub <https://github.com/software-mansion/starknet.py/issues/new?assignees=&labels=bug&projects=&template=bug_report.yaml&title=%5BBUG%5D+%3Ctitle%3E>`_ or contract us on `Starknet Discord server <https://starknet.io/discord>`_ in ``#🐍 | starknet-py`` channel.

.. currentmodule:: starknet_py.net.gateway_client

:class:`GatewayClient` and Gateway / Feeder Gateway API will become deprecated in the future.
    As a result, :class:`GatewayClient` won't work and will eventually be removed. Consider migrating to :ref:`FullNodeClient`.


.. currentmodule:: starknet_py.net.full_node_client

:class:`FullNodeClient` RPC specification has been updated from `v0.3.0-rc1 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.3.0-rc1>`_ to `v0.3.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.3.0>`_.

.. currentmodule:: starknet_py.contract

Also, four methods were added to its interface:

- :meth:`FullNodeClient.get_block_number`
- :meth:`FullNodeClient.get_block_hash_and_number`
- :meth:`FullNodeClient.get_chain_id`
- :meth:`FullNodeClient.get_syncing_status`


0.17.0 Breaking changes
-----------------------

1. Deprecated function ``compute_invoke_hash`` in :mod:`starknet_py.net.models.transaction` has been removed in favor of :func:`starknet_py.hash.transaction.compute_invoke_transaction_hash`.

.. currentmodule:: starknet_py.net.udc_deployer.deployer

2. Removed deprecated ``Deployer.create_deployment_call`` and ``Deployer.create_deployment_call_raw`` in favor of :meth:`Deployer.create_contract_deployment` and :meth:`Deployer.create_contract_deployment_raw`.

3. Removed ``PENDING`` transaction status.


0.17.0 Minor changes
--------------------

.. currentmodule:: starknet_py.contract

1. :meth:`DeclareResult.deploy`, :meth:`PreparedFunctionCall.invoke`, :meth:`PreparedFunctionCall.estimate_fee`, :meth:`ContractFunction.invoke`, :meth:`Contract.declare` and :meth:`Contract.deploy_contract` can now accept custom ``nonce`` parameter.

.. currentmodule:: starknet_py.net.account.account

2. :meth:`Account.sign_invoke_transaction`, :meth:`Account.sign_declare_transaction`, :meth:`Account.sign_declare_v2_transaction`, :meth:`Account.sign_deploy_account_transaction` and :meth:`Account.execute` can now accept custom ``nonce`` parameter.
3. :meth:`Account.get_nonce` can now be parametrized with ``block_number`` or ``block_hash``.
4. :meth:`Account.get_balance` can now be parametrized with ``block_number`` or ``block_hash``.

RPC related changes:

.. currentmodule:: starknet_py.net.client_models

5. :class:`L2toL1Message` dataclass now has an additional field: ``from_address``.
6. :class:`TransactionReceipt` dataclass now has two additional, optional fields: ``type``  and ``contract_address``.

.. currentmodule:: starknet_py.net.full_node_client

7. :meth:`FullNodeClient.get_events` ``keys`` and ``address`` parameters type are now optional.
8. :meth:`FullNodeClient.get_events` ``keys`` parameter can now also accept integers as felts.

.. currentmodule:: starknet_py.net.models

9. :class:`StarknetChainId` changed from ``Enum`` to ``IntEnum``.

.. currentmodule:: starknet_py.net.client

10. :meth:`Client.wait_for_tx` has a new parameter ``retries`` describing the amount of retries before a time out when querying for a transaction.


0.17.0 Deprecations
-------------------
.. currentmodule:: starknet_py.net.client

1. `wait_for_accept` parameter in :meth:`Client.wait_for_tx` and :meth:`SentTransaction.wait_for_acceptance` has been deprecated.


0.17.0 Bugfixes
---------------

.. currentmodule:: starknet_py.hash.class_hash

1. Fixed a bug when :func:`compute_class_hash` mutated the ``contract_class`` argument passed to a function.


|

.. raw:: html

  <hr>

|

**********************
0.16.1 Migration guide
**********************

    Version 0.16.1 of **starknet.py** brings the long-awaited **Windows** support!

Additionally, this release brings support for `RPC v0.3.0rc1 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.3.0-rc1>`_!

0.16.1 Breaking changes
-----------------------

.. currentmodule:: starknet_py.net.full_node_client

1. :meth:`FullNodeClient.get_events` ``keys`` parameter type is now ``List[List[str]]`` instead of ``List[str]``.
2. :meth:`FullNodeClient.get_state_update` return type has been changed from ``StateUpdate`` to ``Union[BlockStateUpdate, PendingBlockStateUpdate]``

.. currentmodule:: starknet_py.net.client_models

3. :class:`StateDiff` dataclass properties have been changed (more details in RPC specification linked above).


0.16.1 Minor changes
--------------------

.. currentmodule:: starknet_py.net.client

1. :meth:`Client.estimate_fee` can take a single transaction or a list of transactions to estimate.


|

.. raw:: html

  <hr>

|

**********************
0.16.0 Migration guide
**********************

    Version 0.16.0 of **starknet.py** comes with support for Python 3.8, 3.9, 3.10 and 3.11!

The ``cairo-lang`` package has been removed as a dependency.

Also, dependencies are now optimized to include only necessary packages.


0.16.0 Bugfixes
---------------

.. currentmodule:: starknet_py.net.udc_deployer.deployer

1. Fixed a bug where :meth:`Deployer.create_contract_deployment_raw` would use a random salt, when ``salt = 0`` was passed.


0.16.0 Breaking changes
-----------------------

.. currentmodule:: starknet_py.net.account.base_account

1. :meth:`BaseAccount.verify_message` is no longer ``async``.

.. currentmodule:: starknet_py.hash.utils

2. Some functions' implementation has been changed to use ``crypto-cpp-py`` package:

   - :func:`pedersen_hash`
   - :func:`private_to_stark_key`
   - :func:`message_signature`
   - :func:`verify_message_signature`

3. Deprecated ``utils.data_transformer`` module has been removed. Use :ref:`Serializers` module instead.

4. Deprecated ``is_felt_pointer`` and ``is_uint256`` functions have been removed. Use :ref:`TypeParser` class instead.
5. Deprecated ``Compiler`` module has been removed. Use an external compilation tool (e.g. Starknet CLI) instead.
6. Deprecated ``compilation_source`` and ``search_paths`` arguments has been removed from several methods. Use ``compiled_contract`` parameter instead.

.. currentmodule:: starknet_py.contract

7. Deprecated ``ContractData.identifier_manager`` has been removed. Use :meth:`ContractData.parsed_abi` instead.

.. currentmodule:: starknet_py.net.signer

8. Removed deprecated ``typed_data`` parameter as dict in :meth:`BaseSigner.sign_message`. Use :ref:`TypedData` dataclass from ``starknet_py.utils.typed_data``.
9. ``starknet_py.utils.crypto`` module has been removed.
10. Changed name of ``starknet_py.transaction_excepions`` to ``starknet_py.transaction_errors`` to match other files.

.. admonition:: Potentially breaking changes
    :class: attention

    Internal code of :meth:`starknet_py.abi.AbiParser.parse` has changed.
    It should not affect users but keep in mind that the Contract can have difficulties resolving ABI.
    If so, please report.

|

.. raw:: html

  <hr>

|

**********************
0.15.0 Migration guide
**********************

0.15.0 adds initial support for Starknet 0.11.0 and related changes.
It also makes the first step to remove the cairo-lang package as starknet.py dependency!

Some classes/functions from cairo-lang package are rewritten and are a part of starknet.py:

- :ref:`transaction dataclasses <Transaction dataclasses>`
- ``get_selector_from_name`` and ``get_storage_var_address`` functions
- ``DeclaredContract`` is now :ref:`ContractClass <ContractClass>`
- ``compute_class_hash`` function


Python version
--------------

Unfortunately, as a result of adaptation to support `cairo-lang` newest package, **support for Python 3.8.X has been dropped**.
The only supported Python version is 3.9.


0.15.0 Deprecations
-------------------

- ``compute_invoke_hash`` is deprecated in favour of ``compute_transaction_hash``
- ``starknet_py.common.create_contract_class`` is deprecated in favour of ``starknet_py.common.create_compiled_contract``
- Client :meth:`~starknet_py.net.client.Client.net` property.
- :meth:`~starknet_py.net.udc_deployer.deployer.Deployer.create_deployment_call` is deprecated in favour of :meth:`~starknet_py.net.udc_deployer.deployer.Deployer.create_contract_deployment`


0.15.0 Breaking changes
-----------------------

1. ``InvokeFunction`` is replaced by the ``Invoke`` dataclass (behaviour is the same, just the name is changed).

2. Removed from client_models.py:

   - Invoke,
   - InvokeFunction,
   - StarknetTransaction,
   - AccountTransaction,
   - ContractClass,
   - Declare,
   - DeployAccount.

3. Transaction's ``tx_type`` field is renamed to ``type``.

4. The ``types.py`` is removed (outdated file containing only imports):

   - import ``decode_shortstring`` and ``encode_shortstring`` from ``starknet_py.cairo.felt``,
   - import ``Invoke`` and ``Transaction`` from ``starknet_py.net.models.transaction``,
   - import ``parse_address`` from ``starknet_py.net.models.address``,
   - import ``net_address_from_net`` from ``starknet_py.net.networks``.

5. Changes in the location of some of the functions:
    .. list-table::
       :widths: 25 25 50
       :header-rows: 1

       * - Function
         - Old Path
         - New Path
       * - compute_address
         - starknet_py.net.models.address
         - starknet_py.hash.address
       * - compute_transaction_hash, compute_deploy_account_transaction_hash, compute_declare_transaction_hash
         - starknet_py.utils.crypto.transaction_hash
         - starknet_py.hash.transaction
       * - compute_hash_on_elements
         - starknet_py.utils.crypto.facade
         - starknet_py.hash.utils
       * - message_signature
         - starknet_py.utils.crypto.facade
         - starknet_py.hash.utils
       * - pedersen_hash
         - starknet_py.utils.crypto.facade
         - starknet_py.hash.utils
       * -
         -
         -
       * - compute_class_hash
         - starkware.starknet.core.os.class_hash
         - starknet_py.hash.class_hash
       * - get_selector_from_name
         - starkware.starknet.public.abi
         - starknet_py.hash.selector
       * - get_storage_var_address
         - starkware.starknet.public.abi
         - starknet_py.hash.storage

6. Removed deprecated ``AccountClient``
7. Removed support for making transactions with version 0.

   - Removed ``Deploy`` transaction.
   - Removed deprecated ``make_declare_tx``.

8. Removed ``client`` argument from Contract :meth:`~starknet_py.contract.Contract.__init__` and :meth:`~starknet_py.contract.Contract.from_address`. Use ``provider`` argument instead.
9. Removed ``net.l1`` L1<>L2 messaging module.
10. Added `chain_id` argument to BaseAccount interface and implementation :meth:`~starknet_py.net.account.base_account.BaseAccount.get_balance` method.
11. Changed Client :meth:`~starknet_py.net.client.Client.get_class_by_hash` return type to ``Union[ContractClass, SierraContractClass]``.
12. Replaced ``contract_address`` with ``sender_address`` in:

    - :class:`starknet_py.net.client_models.InvokeTransaction`
    - :class:`starknet_py.net.models.transaction.Invoke`
    - ``compute_invoke_hash``
13. Replaced ``BlockStateUpdate.state_diff.declared_contract_hashes`` is now a list of ``DeclaredContractHash`` representing new Cairo classes. Old declared contract classes are still available at ``BlockStateUpdate.state_diff.deprecated_declared_contract_hashes``.
14. Removed ``version`` property from ``PreparedFunctionCall`` class.
15. Removed deprecated ``max_steps`` in :class:`~starknet_py.proxy.contract_abi_resolver.ProxyConfig`.
16. Removed ``supported_transaction_version`` property from ``BaseAccount`` abstract class.


Transaction dataclasses
-----------------------

All transaction's dataclasses can be imported from the ``starknet_py.net.models.transaction`` module.
The main differences between them and those from the Cairo-lang:

- ``tx_type`` field is renamed to ``type``,
- fields are not validated while creating.

All of them can be used as usual.


ContractClass
-------------

``DeclaredContract`` has been renamed to ``ContractClass``.
There also exists ``CompiledContract`` dataclass, which specifies **abi** attribute to be required.

|

.. raw:: html

  <hr>

|

**********************
0.14.0 Migration guide
**********************

This version deprecates several modules and fixes underlying issues with several others.

0.14.0 Breaking changes
-----------------------

1. Renamed first parameter of :class:`~starknet_py.net.udc_deployer.deployer.ContractDeployment` from ``udc`` to ``call``, that is returned from :meth:`~starknet_py.net.udc_deployer.deployer.Deployer.create_deployment_call`.


0.14.0 Deprecations
-------------------

1. `compiler` module. It will be removed in the future. We recommend transitioning to building contracts through Starknet CLI or external tools and using only compiled contracts with starknet.py.
2. ``utils.data_transformer`` module. It has been replaced with :ref:`serializers` module.


Serializers module
------------------

New :ref:`serializers` module has been added in place of old ``data_transformer``. See :ref:`Serialization` guide for more details.


auto_estimate
-------------

The way **automatic fee estimation is calculated** has changed from

``transaction estimated fee * 1.1``

to

``transaction estimated fee * 1.5``

when using ``auto_estimate`` parameter in API functions (for example :meth:`~starknet_py.net.account.account.Account.execute`, :meth:`~starknet_py.net.account.account.Account.sign_invoke_transaction` or :meth:`~starknet_py.contract.PreparedFunctionCall.invoke`).
It was caused by many transactions failing due to low ``max_fee``.

.. note::
    It is now possible to set the value by which the estimated fee is multiplied,
    by changing ``ESTIMATED_FEE_MULTIPLIER`` in :class:`~starknet_py.net.account.account.Account`.

|

.. raw:: html

  <hr>

|

**********************
0.13.0 Migration guide
**********************

This version deprecates the :class:`AccountClient <starknet_py.net.account.AccountClient>`, which is a major change to the starknet.py.
It is replaced with new :class:`BaseAccount <starknet_py.net.account.base_account.BaseAccount>` ABC and its
default implementation :class:`Account <starknet_py.net.account.account.Account>`.

Unlike ``AccountClient``, an ``Account`` is not a :class:`Client <starknet_py.net.client.Client>` anymore. This means that methods like
``get_storage_at``, ``call_contract`` etc. are not available in the Account interface.

However, ``Account`` now exposes a ``.client`` property, which means using an ``Account`` is
just as simple as ``AccountClient`` was. For example:

.. literalinclude:: ../starknet_py/tests/e2e/docs/migration_guide/test_account_comparison.py
    :language: python
    :dedent: 4
    :start-after: docs-1: start
    :end-before: docs-1: end

.. literalinclude:: ../starknet_py/tests/e2e/docs/migration_guide/test_account_comparison.py
    :language: python
    :dedent: 4
    :start-after: docs-2: start
    :end-before: docs-2: end

.. literalinclude:: ../starknet_py/tests/e2e/docs/migration_guide/test_account_comparison.py
    :language: python
    :dedent: 4
    :start-after: docs-3: start
    :end-before: docs-3: end

Replacing inheritance with composition simplifies the ``Account`` interface and will make
maintaining ``Account`` simpler.

Changes in the Account interface
--------------------------------

1. Removed ``hash_message`` method. Use :meth:`TypedData.message_hash <starknet_py.utils.typed_data.TypedData.message_hash>` directly instead.
2. ``Account`` doesn't expose a ``net`` property.
3. ``Account`` doesn't accept a ``supported_tx_version`` parameter. It currently always uses version 1.
4. Some parameters like ``max_fee`` or ``auto_estimate`` are now keyword only arguments. They have to be explicitly named like ``account.sign_invoke_transaction(Call(...), max_fee=1000)``. Writing ``account.sign_invoke_transaction(Call(...), 1000)`` will not work.


0.13.0 Deprecations
-------------------

1. Passing a dict to ``BaseSigner.sign_message`` as parameter has been deprecated in favor of :class:`TypedData <starknet_py.utils.typed_data.TypedData>` dataclass.
2. Argument ``client`` of ``Contract`.__init__` and ``Contract.from_address`` has been deprecated and replaced with ``provider``.
3. Starknet <> Ethereum Messaging module has been deprecated.
4. ``PreparedFunctionCall.arguments`` has been deprecated to simplify the upcoming ``serialization`` module.


0.13.0 Breaking changes
-----------------------

1. ``version`` parameter has been removed from the most ``Contract`` methods. ``Contract`` will now use version that the ``Account`` or ``AccountClient`` is using.
2. ``DeclareResult`` now only accepts :class:`BaseAccount <starknet_py.net.account.base_account.BaseAccount>`.
3. ``invoke_tx`` has been removed from the ``Client.call_contract`` parameters. ``call`` should be used instead.
4. All error messages have been standardized with capitalization at the beginning and a full stop at the end.

|

.. raw:: html

  <hr>

|

**********************
0.12.0 Migration guide
**********************

starknet.py 0.12.0 brings support for the Cairo-lang 0.10.3 and the new TESTNET2 chainId.

0.12.0 Breaking Changes
-----------------------

There should not be any breaking changes if you are using the `StarknetChainId` imported from the `starknet_py.net.models`,
but if you are importing it from the Cairo-lang package, please switch to the one from starknet.py.

|

.. raw:: html

  <hr>

|

**********************
0.11.0 Migration guide
**********************

Cairo-lang 0.10.3 dropped support for the `Deploy` transaction. To be compatible we had to remove some deprecated features.

0.11.0 Breaking Changes
-----------------------

Removed APIs:

- `Contract.deploy`. Read more about deployment in the `Deploying contracts <https://starknetpy.readthedocs.io/en/latest/guide.html#deploying-contracts>`_ section.
- `AccountClient.create_account`. `Account creation <https://starknetpy.readthedocs.io/en/latest/account_creation.html>`_ docs are here to help you!
- `Client.deploy` method (from the interface and all implementations)
- `make_deploy_tx`
- `compute_deploy_hash`
- the `Deploy` transaction


Invoke Transaction
------------------

Old `InvokeFunction` transaction is now aliased as `Invoke`. We suggest to start using the new `Invoke`.

|

.. raw:: html

   <hr>

|

**********************
0.9.0 Migration guide
**********************

starknet.py 0.9.0 brings support for `RPC 0.2.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.2.0>`_,
updates :meth:`Contract.from_address` method to work with the newest proxies and removes some deprecated features.

0.9.0 Breaking Changes
----------------------

- Removed deprecated `Account.sign_transaction`. Use new `Account.sign_invoke_transaction`.
- Removed deprecated `InvokeFunction` as `call_contract` parameter. Use `Call` class instead.
- `StateDiff` has `declared_contract_hashes` instead of `declared_contracts` field (only name has changed).
- Support for RPC 0.1.0 has been dropped in favour of RPC 0.2.0.


Contract.from_address
---------------------

Check out the Guide with the new section :ref:`Resolving proxy contracts` to see how to easily use proxies with the starknet.py.

|

.. raw:: html

  <hr>

|

**********************
0.8.0 Migration guide
**********************

Cairo-lang 0.10.1 brings support for `DEPLOY_ACCOUNT` transactions that will completely
replace currently used `DEPLOY` transactions sometime in the future.

You should already modify your applications to use new deployment flow to either support deployments
using new flow:

1. Declare a contract on Starknet using `Declare` transaction
2. Pre-fund the address of new account with enough tokens to cover transaction costs
3. Send a `DeployAccount` transaction with the pre-funded address

or support deploying through syscall or `Universal Deployer Contract <https://community.starknet.io/t/universal-deployer-contract-proposal/1864>`_.

0.8.0 Breaking Changes
----------------------

- `entry_point_selector` has been removed from `v1` transactions. `InvokeTransaction`'s field has been changed to `Optional[int]`
- `net.models.address.compute_address` signature has been changed and use of keyword arguments is now mandatory
- `Client.estimate_fee` ABC now also accepts `DeployAccount` transaction as `tx` parameter. Custom clients should be updated to reflect this change.


0.8.0 Deprecations
------------------

- `Contract.deploy` has been deprecated in favor of new `DeployAccount` flow
- `Client.deploy` has been deprecated

|

.. raw:: html

  <hr>

|

**********************
0.5.0 Migration guide
**********************

``cairo-lang`` 0.10.0 brings a lot of new exciting changes, like:

- new cairo syntax,
- new transaction version (1),
- new ``__validate__`` endpoint in accounts.

``starknet.py`` 0.5.0 has an experimental support for new features and tries to minimize number of breaking changes for
users who want to use the old transaction version (0). Please note that support for this transaction version will be
removed in the future.

.. note::

    There is no need to upgrade ``starknet.py`` to the newest version because the old one is still compatible with Starknet.
    However, an upgrade is required to use the new features.


0.5.0 Breaking Changes
-----------------------

New Cairo syntax
^^^^^^^^^^^^^^^^^^^^^^^

With the update of `cairo-lang <https://github.com/starkware-libs/cairo-lang>`_ to version ``0.10.0``,
the syntax of contracts written in cairo changes significantly.
You can see the new syntax `here <https://starkware.notion.site/starkware/StarkNet-0-10-0-4ac978234c384a30a195ce4070461257#8bfeb76259234f32b5f42376f0d976b9>`_.

As a result, the **old syntax is no longer supported**.

.. note::

    This only applies to you if you compile your cairo programs using starknet.py. If you use
    programs that are already compiled you don't need to worry.


For the already existent programs to be compatible with the new Starknet version,
they would have to be migrated using ``cairo-migrate`` command from CLI. It is a part of `cairo-lang` package.

To migrate old syntax to the old one in place run:

.. code-block::

    > cairo-migrate FILES_LIST -i

See `cairo-lang release notes <https://github.com/starkware-libs/cairo-lang/releases>`_ for more details about
the new syntax.

Python versions
^^^^^^^^^^^^^^^

We drop support for python 3.7.X, following `cairo-lang` support. You must use python 3.8+ to use starknet.py 0.5.0.

InvokeFunction and Declare
^^^^^^^^^^^^^^^^^^^^^^^^^^

A new required parameter, ``nonce``, was added to them. Use ``None`` for transaction version = 0 and a proper nonce value for
new transaction version = 1.

New Transaction version
-----------------------

Cairo 0.10.0 brings a transaction version = 1:

- `Deploy` transactions are no longer available,
- user accounts need to have `__validate__` and `__validate_declare__` functions,
- transactions have different fields,
- contracts have a native nonce field available.

You can still use the old transaction version, but please note it will be removed in the future. Please refer to deprecation
warnings to see required changes.

For now both (0 nad 1) transaction versions will be accepted but there will be a ``DeprecationWarning`` while using version 0.

AccountClient constructor
-------------------------

AccountClient's constructor has a new parameter now. ``supported_tx_version`` is used to differentiate between old and new accounts.
It is set to 0 as default so there is no need to set it while using old account.

.. note::

    In the future versions default value of ``supported_tx_version`` will be changed to 1. This will happen when transaction version = 0 is removed.

Deprecated Features
-------------------

InvokeFunction as call_contract parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``InvokeFunction`` has been deprecated as a call_contract parameter. Users should use ``Call`` instead.

Transaction version 0
^^^^^^^^^^^^^^^^^^^^^

Although transactions version 0 are still valid, users should switch to Accounts supporting transaction version 1.

AccountClient's methods
^^^^^^^^^^^^^^^^^^^^^^^

The following :ref:`AccountClient`'s methods has been deprecated:

- :meth:`~starknet_py.net.account.account_client.AccountClient.prepare_invoke_function`, :meth:`~starknet_py.net.account.account_client.AccountClient.sign_invoke_transaction` should be used instead.
- :meth:`~starknet_py.net.account.account_client.AccountClient.sign_transaction`, :meth:`~starknet_py.net.account.account_client.AccountClient.sign_invoke_transaction` should be used instead.

Unsigned declare transaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``make_declare_tx`` is deprecated, because in the future versions of Starknet unsigned declare transactions will not be
supported. :meth:`~starknet_py.net.account.account_client.AccountClient.sign_declare_transaction` should be used to create
and sign declare transaction.

Deploy transaction
^^^^^^^^^^^^^^^^^^

Deploy transactions will not be supported in the future versions of Starknet, so ``make_deploy_tx`` is deprecated.
Contracts should be deployed through cairo syscall.

|

.. raw:: html

  <hr>

|

**********************
0.4.0 Migration guide
**********************

0.4.0 of starknet.py brings multiple changes including breaking changes to API.
To ensure smooth migration to this version please familiarize yourself with this
migration guide.

Overlook of the changes
-----------------------

0.4.0 brings support for the `Starknet rpc interface <https://github.com/starkware-libs/starknet-specs/blob/606c21e06be92ea1543fd0134b7f98df622c2fbf/api/starknet_api_openrpc.json>`_.

This required us to introduce some big changes to the clients. API methods has
remained mostly the same, but their parameters changed. Also, we've introduced custom dataclasses
for every endpoint, that are simplified from these from ``cairo-lang`` library.

This provides uniform interface for both Starknet gateway (only supported way of interacting with
Starknet in previous starknet.py versions), as well as JSON-RPC.

Clients
-------

Client has been separated into two specialized modules.

* Use :ref:`GatewayClient` to interact with Starknet like you did in previous starknet.py versions
* Use :ref:`FullNodeClient` to interact with JSON-RPC

.. note::

    It is no longer possible to create an instance of ``Client``. Doing so will cause
    errors in runtime.

API Changes
-----------

Client methods has had some of the parameters removed, so it provided uniform interface
for both gateway and rpc methods. Please refer to :ref:`GatewayClient` and :ref:`FullNodeClient`
to see what has changed.
There is no longer add_transaction method in the Client interface. It was renamed to send_transaction.

.. note::

    Please note that send_transaction only sends a transaction, it doesn't sign it, even when using AccountClient.

Sending transactions
--------------------

Sending transactions is currently only supported in ``GatewayClient``. We've also changed the flow
of creating transactions through clients:

``Client.deploy`` and ``Client.declare`` no longer accept contract source as their input.
Instead they require a prepared transactions. These can be created using ``Transactions`` module

.. code-block:: python

    from starknet_py.transactions.declare import make_declare_tx

    client = GatewayClient("testnet")

    contract_source_code = "..."
    declare_tx = make_declare_tx(compilation_source=contract_source_code)
    await client.declare(declare_tx)

Interface of :ref:`Contract` remains unchanged and it is still the recommended way of using starknet.py

AccountClient
-------------

:ref:`AccountClient` now implements Client interface: parameters of some of its methods were changed.
It also doesn't have add_transaction method (like the rest of the clients).

Quick summary about the new methods:

- prepare_invoke_function - it can be used to create InvokeFunction from one or few calls (without signature)
- sign_transaction - takes list of calls and creates signed InvokeFunction from them
- send_transaction - implements Client interface (takes Invoke function and sends it without changes)
- execute - can take list of calls, sign them and send

Client errors changes
---------------------

`BadRequest` class has been removed and replaced with :ref:`Client errors` module and
:class:`starknet_py.net.client_errors.ClientError` or more specified errors can now
be used for handling client errors.
See :ref:`Handling client errors` in guide for an example.

Facade.py
---------

`sign_calldata` method has been removed entirely. See guide on how how you can
now prepare and send transactions to Starknet.

Contract changes
----------------

Transaction's status is not checked while invoking through Contract interface, because RPC write API doesn't return "code"
parameter. To check if the transaction passed use wait_for_acceptance on InvokeResult.
