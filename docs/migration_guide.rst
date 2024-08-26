Migration guide
===============

******************************
0.24.1 Migration guide
******************************
This version contains a quick fix to parsing ABI for Cairo v2 contracts. Due to new release of compiler, `u96` is now compiled to `BoundedInt` in ABI.

0.24.1 Minor changes
--------------------

1. Fixed parsing ABI that contains `u96` data type.
2. Fixed `l1_address` deserialization in `L2toL1MessageSchema`.

******************************
0.24.0 Migration guide
******************************

.. currentmodule:: starknet_py.devnet_utils.devnet_client

1. :class:`DevnetClient` has been implemented to interact with additional features of the `starknet-devnet-rs <https://github.com/0xSpaceShard/starknet-devnet-rs>`_

.. currentmodule:: starknet_py.net.signer.ledger_signer

2. :class:`LedgerSigner` has been implemented to enable signing with Ledger hardware wallet

0.24.0 Targeted versions
------------------------

- Starknet - `0.13.1.1 <https://docs.starknet.io/documentation/starknet_versions/version_notes/#version0.13.1.1>`_
- RPC - `0.7.1 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.7.1>`_

0.24.0 Breaking changes
-----------------------

.. currentmodule:: starknet_py.net.client_models

1. :class:`CompiledContract` and :class:`ContractClass` have been renamed to :class:`DeprecatedCompiledContract` and :class:`DeprecatedContractClass`.
2. :class:`ContractClassSchema` have been renamed to :class:`DeprecatedContractClassSchema`

******************************
0.23.0 Migration guide
******************************

Version 0.23.0 of **starknet.py** comes with support for `SNIP-12 <https://github.com/starknet-io/SNIPs/blob/main/SNIPS/snip-12.md>`_!

0.23.0 Targeted versions
------------------------

- Starknet - `0.13.1.1 <https://docs.starknet.io/documentation/starknet_versions/version_notes/#version0.13.1.1>`_
- RPC - `0.7.1 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.7.1>`_

0.23.0 Breaking changes
-----------------------

.. currentmodule:: starknet_py.utils.typed_data

1. :class:`StarkNetDomain` has been renamed to :class:`Domain`
2. :class:`TypedData` field ``domain`` has been changed from ``dict`` to :class:`Domain`
3. :class:`Parameter` is now abstract - :class:`StandardParameter`, :class:`EnumParameter` and :class:`MerkleTreeParameter` should be used

0.23.0 Minor changes
-----------------------

.. currentmodule:: starknet_py.net.account.account

1. :meth:`Account.sign_message` now accepts parameter ``typed_data`` as both :class:`~starknet_py.utils.typed_data.TypedData` and :class:`~starknet_py.net.models.typed_data.TypedDataDict`
2. :meth:`Account.verify_message` now accepts parameter ``typed_data`` as both  :class:`~starknet_py.utils.typed_data.TypedData` and :class:`~starknet_py.net.models.typed_data.TypedDataDict`
3. :meth:`~starknet_py.net.signer.stark_curve_signer.KeyPair.from_keystore` has been added

******************************
0.22.0 Migration guide
******************************

0.22.0 Targeted versions
------------------------

- Starknet - `0.13.1.1 <https://docs.starknet.io/documentation/starknet_versions/version_notes/#version0.13.1.1>`_
- RPC - `0.7.1 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.7.1>`_

0.22.0 Breaking changes
-----------------------

1. Support for Goerli has been removed

.. currentmodule:: starknet_py.net.models

2. ``StarknetChainId.SEPOLIA_TESTNET`` has been renamed to :class:`StarknetChainId.SEPOLIA`

.. currentmodule:: starknet_py.net.account.account

3. Parameter ``chain`` has been removed from the methods :meth:`Account.deploy_account_v1` and :meth:`Account.deploy_account_v3`
4. Parameter ``chain_id`` has been removed from the method :meth:`~Account.get_balance`
5. :class:`~starknet_py.net.client_models.L1HandlerTransactionTrace` field ``execution_resources`` is now required


******************************
0.21.0 Migration guide
******************************

Version 0.21.0 of **starknet.py** comes with support for RPC 0.7.0!

0.21.0 Targeted versions
------------------------

- Starknet - `0.13.1 <https://docs.starknet.io/documentation/starknet_versions/version_notes/#version0.13.1>`_
- RPC - `0.7.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.7.0>`_

0.21.0 Breaking changes
-----------------------

.. currentmodule:: starknet_py.net.client_models

1. :class:`PendingStarknetBlock` and :class:`PendingStarknetBlockWithTxHashes` field ``parent_block_hash`` has been renamed to ``parent_hash``
2. :class:`StarknetBlockCommon` has been renamed to :class:`BlockHeader`
3. :class:`StarknetBlock` and :class:`StarknetBlockWithTxHashes` fields ``parent_block_hash`` and ``root`` have been renamed to ``parent_hash`` and ``new_root`` respectively
4. :class:`FunctionInvocation` field ``execution_resources`` has been renamed to ``computation_resources``

0.21.0 Minor changes
-----------------------

1. :class:`EventsChunk` field ``events`` is now a list of :class:`EmittedEvent` instead of :class:`Event`
2. :class:`ExecutionResources` has a new required field ``data_availability``
3. :class:`InvokeTransactionTrace`, :class:`DeclareTransactionTrace` and :class:`DeployAccountTransactionTrace` have a new required field ``execution_resources``
4. :class:`EstimatedFee` has new required fields ``data_gas_consumed`` and ``data_gas_price``
5. :class:`StarknetBlock`, :class:`PendingStarknetBlock`, :class:`StarknetBlockWithTxHashes`, :class:`PendingStarknetBlockWithTxHashes` have new required fields ``l1_data_gas_price`` and ``l1_da_mode``
6. :class:`SierraContractClass` has an additional propery ``parsed_abi``

**********************
0.20.0 Migration guide
**********************

    Version 0.20.0 of **starknet.py** comes with support for Python 3.12!

0.20.0 Targeted versions
------------------------

- Starknet - `0.13.0 <https://docs.starknet.io/documentation/starknet_versions/version_notes/#version0.13.0>`_
- RPC - `0.6.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.6.0>`_

0.20.0 Breaking changes
-----------------------

1. Type of ``l1_handler`` in :class:`~starknet_py.abi.v2.model.Abi` model class for Cairo 2 has been changed from ``Function`` to ``Dict[str, Function]``
2. In :ref:`Abi` module the code related to Cairo 0 has been moved from ``starknet_py.abi`` to ``starknet_py.abi.v0``
3. :class:`StarknetEthProxyCheck` has been removed from the Proxy checks

**********************
0.19.0 Migration guide
**********************

Version 0.19.0 of **starknet.py** comes with support for RPC 0.6.0!

.. currentmodule:: starknet_py.net.client_models

New classes added to mirror the recent changes in the RPC v0.6.0 specification include:
:class:`ResourceBoundsMapping`, :class:`ResourceBounds`, :class:`PriceUnit`, :class:`FeePayment`, :class:`DAMode`.

Changes in the :class:`~starknet_py.net.account.account.Account`:

.. currentmodule:: starknet_py.net.account.account

- :meth:`~Account.execute` has been renamed to :meth:`~Account.execute_v1`
- :meth:`~Account.execute_v3` has been added
- :meth:`~Account.deploy_account` has been renamed to :meth:`~Account.deploy_account_v1`
- :meth:`~Account.deploy_account_v3` has been added
- :meth:`~Account.sign_declare_v3`, :meth:`~Account.sign_deploy_account_v3` and :meth:`~Account.sign_invoke_v3` have been added
- :meth:`sign_declare_transaction`, :meth:`sign_declare_v2_transaction`, :meth:`sign_deploy_account_transaction` and :meth:`sign_invoke_transaction` have been renamed to :meth:`~Account.sign_declare_v1`, :meth:`~Account.sign_declare_v2`, :meth:`~Account.sign_deploy_account_v1` and :meth:`~Account.sign_invoke_v1` respectively

All new functions with ``v3`` in their name operate similarly to their ``v1`` and ``v2`` counterparts.
Unlike their ``v1`` counterparts however, ``v3`` transaction fees are paid in Fri (10^-18 STRK). Therefore,  ``max_fee`` parameter, which is typically set in Wei, is not applicable for ``v3`` functions. Instead, ``l1_resource_bounds`` parameter is utilized to limit the Fri amount used.
The same applies to the new ``v3`` methods in the :class:`~starknet_py.contract.Contract` class.

Changes in the :class:`~starknet_py.net.full_node_client.FullNodeClient`:

.. currentmodule:: starknet_py.net.full_node_client

- :meth:`~FullNodeClient.estimate_fee` has a new parameter ``skip_validate``
- :meth:`~FullNodeClient.declare` accepts ``transaction`` argument of the type :class:`~starknet_py.net.models.transaction.DeclareV3`
- :meth:`~FullNodeClient.send_transaction` accepts ``transaction`` argument of the type :class:`~starknet_py.net.models.transaction.InvokeV3`
- :meth:`~FullNodeClient.deploy_account` accepts ``transaction`` argument of the type :class:`~starknet_py.net.models.transaction.DeployAccountV3`

Changes in the :class:`~starknet_py.contract.Contract`:

.. currentmodule:: starknet_py.contract

- :meth:`Contract.declare` has been replaced by :meth:`Contract.declare_v1`, :meth:`Contract.declare_v2` and :meth:`Contract.declare_v3`
- :meth:`Contract.deploy_contract` has been replaced by :meth:`Contract.deploy_contract_v1` and :meth:`Contract.deploy_contract_v3`. Optional parameters ``unique`` and ``salt`` have been added to both methods
- :meth:`ContractFunction.prepare` has been replaced by :meth:`ContractFunction.prepare_invoke_v1`, :meth:`ContractFunction.prepare_invoke_v3` and :meth:`ContractFunction.prepare_call`
- :meth:`ContractFunction.invoke` has been replaced by :meth:`ContractFunction.invoke_v1` and :meth:`ContractFunction.invoke_v3`
- :meth:`PreparedFunctionCall` has now only methods :meth:`PreparedFunctionCall.call` and :meth:`PreparedFunctionCall.call_raw`
- :meth:`PreparedFunctionInvokeV1` and :meth:`PreparedFunctionInvokeV3` with methods ``invoke`` and ``estimate_fee`` have been added
- :meth:`DeclareResult.deploy` has been replaced by :meth:`DeclareResult.deploy_v1` and :meth:`DeclareResult.deploy_v3`

0.19.0 Targeted versions
------------------------

- Starknet - `0.13.0 <https://docs.starknet.io/documentation/starknet_versions/version_notes/#version0.13.0>`_
- RPC - `0.6.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.6.0>`_

0.19.0 Breaking changes
-----------------------
Other breaking changes not mentioned above.

.. currentmodule:: starknet_py.net.client_models

1. :class:`GatewayClient` all related classes and fields have been removed.
2. Client ``net`` property has been removed.
3. :class:`Declare`, :class:`DeployAccount` and :class:`Invoke` have been renamed to :class:`~starknet_py.net.models.transaction.DeclareV1`, :class:`~starknet_py.net.models.transaction.DeployAccountV1` and :class:`~starknet_py.net.models.transaction.InvokeV1` respectively.
4. :class:`TransactionReceipt` field ``execution_resources`` has been changed from ``dict`` to :class:`ExecutionResources`.
5. :class:`TransactionReceipt` fields ``status`` and ``rejection_reason`` have been removed.
6. :class:`TransactionStatus`, :class:`TransactionExecutionStatus` and :class:`TransactionFinalityStatus` have been changed to have the same structure as in RPC specification.
7. :class:`EstimatedFee` has a new required field ``unit``.
8. :class:`EstimatedFee` field ``gas_usage`` has been renamed to ``gas_consumed``.
9. :class:`FunctionInvocation` has a new required field ``execution_resources``.
10. :class:`ResourcePrice` field ``price_in_strk`` has been renamed to ``price_in_fri`` and has now become required.
11. :class:`ResourceLimits` class has been renamed to :class:`ResourceBounds`.
12. :class:`~starknet_py.net.account.base_account.BaseAccount` and :class:`~starknet_py.net.account.account.Account` property ``supported_transaction_version`` has been removed.
13. ``wait_for_accept`` parameter in :meth:`Client.wait_for_tx` and :meth:`SentTransaction.wait_for_acceptance` has been removed.
14. :class:`InvokeTransaction` has been replaced by :class:`InvokeTransactionV0` and :class:`InvokeTransactionV1`.
15. :class:`DeclareTransaction` has been replaced by :class:`DeclareTransactionV0`, :class:`DeclareTransactionV1` and :class:`DeclareTransactionV3`.
16. :class:`DeployAccountTransaction` has been replaced by :class:`DeployAccountTransactionV1`.

0.19.0 Minor changes
--------------------

1. :class:`L1HandlerTransaction` field ``nonce`` is now required.
2. :class:`TransactionReceipt` fields ``actual_fee``, ``finality_status``, ``execution_status``, ``execution_resources`` and ``type`` are now required.

0.19.0 Development-related changes
----------------------------------

Test execution has been transitioned to the new `starknet-devnet-rs <https://github.com/0xSpaceShard/starknet-devnet-rs>`_.
To adapt to this change, it should be installed locally and added to the ``PATH``. Further information regarding this change can be found in the `Development <https://starknetpy.readthedocs.io/en/latest/development.html>`_ section.

**********************
0.18.3 Migration guide
**********************

Version 0.18.3 of **starknet.py** comes with support for RPC 0.5.1!


0.18.3 Targeted versions
------------------------

- Starknet - `0.12.2 <https://community.starknet.io/t/introducing-p2p-authentication-and-mismatch-resolution-in-v0-12-2/97993>`_
- RPC - `0.5.1 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.5.1>`_


0.18.3 Breaking changes
-----------------------

1. Support for ``TESTNET2`` network has been removed.

.. currentmodule:: starknet_py.net.client

2. :meth:`FullNodeClient.get_pending_transactions` method has been removed. It is advised to use :meth:`FullNodeClient.get_block` method with ``block_number="pending"`` argument.

.. currentmodule:: starknet_py.net.client_models

3. :class:`PendingStarknetBlock` field ``parent_hash`` is now named ``parent_block_hash``.
4. :class:`FunctionInvocation` fields ``events`` and ``messages`` have been changed from ``List[Event]`` and ``List[L2toL1Message]`` to ``List[OrderedEvent]`` and ``List[OrderedMessage]`` respectively.
5. ``cairo_version`` parameter in :meth:`Account.sign_invoke_transaction` and :meth:`Account.execute` has been removed.

0.18.3 Minor changes
--------------------

1. :class:`StarknetBlock`, :class:`StarknetBlockWithTxHashes`, :class:`PendingStarknetBlock` and :class:`PendingStarknetBlockWithTxHashes` now have two additional fields: ``starknet_version`` and ``l1_gas_price``.
2. :class:`PendingStarknetBlock` and :class:`PendingStarknetBlockWithTxHashes` fields ``timestamp``, ``sequencer_address`` and ``parent_block_hash`` are now required, not optional.
3. :class:`TransactionReceipt` now has an additional field - ``message_hash`` (for ``L1_HANDLER_TXN_RECEIPT``).
4. Most fields in ``TransactionTrace`` classes are now optional.
5. :class:`InvokeTransactionTrace`, :class:`DeclareTransactionTrace`, :class:`DeployAccountTransactionTrace` and :class:`L1HandlerTransactionTrace` classes now have an additional field - ``state_diff``.


|

.. raw:: html

  <hr>

|

**********************
0.18.2 Migration guide
**********************

Version 0.18.2 of **starknet.py** comes with support of `RPC v0.4.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.4.0>`_ Trace API!
Additionally, you can now `properly` use Cairo1 accounts! ``starknet.py`` automatically checks if your account is in Cairo1 and
sets the calldata encoding accordingly.

0.18.2 Targeted versions
------------------------

- Starknet - `0.12.2 <https://community.starknet.io/t/introducing-p2p-authentication-and-mismatch-resolution-in-v0-12-2/97993>`_
- RPC - `0.4.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.4.0>`_

0.18.2 Breaking changes
-----------------------

.. currentmodule:: starknet_py.net.client

1. :meth:`Client.get_block_traces` has been renamed to :meth:`Client.trace_block_transactions` in order to match RPC specification.


0.18.2 Deprecations
-------------------

.. currentmodule:: starknet_py.net.account.account

1. ``cairo_version`` parameter in :meth:`Account.sign_invoke_transaction` and :meth:`Account.execute` has been deprecated.


0.18.2 Bugfixes
---------------

.. currentmodule:: starknet_py.contract

1. Fixed a bug when using ``proxy_config=True`` in :meth:`Contract.from_address` method regarding ``Entry point EntryPointSelector(...) not found in contract``.

0.18.2 Minor changes
--------------------

1. :meth:`Client.trace_block_transactions` return type has been changed from ``BlockTransactionTraces`` to ``Union[BlockTransactionTraces, List[BlockTransactionTrace]]``.

.. currentmodule:: starknet_py.net.gateway_client

2. ``include_block`` parameter in :meth:`GatewayClient.get_state_update` now works on gateway mainnet.

.. currentmodule:: starknet_py.net.account.account

3. :class:`BaseAccount` interface and :class:`Account` now have an additional **async** property - ``cairo_version``.


0.18.2 Development-related changes
----------------------------------

1. In order to be able to run tests, you must set some environmental variables:

    - ``INTEGRATION_RPC_URL``
    - ``TESTNET_RPC_URL``
    - ``INTEGRATION_ACCOUNT_PRIVATE_KEY``
    - ``INTEGRATION_ACCOUNT_ADDRESS``
    - ``TESTNET_ACCOUNT_PRIVATE_KEY``
    - ``TESTNET_ACCOUNT_ADDRESS``

The best way to do that is to create ``test-variables.env`` file in ``starknet_py/tests/e2e/`` directory, so they can be loaded by the ``python-dotenv`` library.
You can find an example file ``test-variables.env.template`` in the same directory with the format of how it should look like.


|

.. raw:: html

  <hr>

|

**********************
0.18.1 Migration guide
**********************

.. currentmodule:: starknet_py.net.gateway_client

This version contains a quick fix to :meth:`GatewayClient.get_state_update` method (mainnet wasn't updated to 0.12.2 then).

.. currentmodule:: starknet_py.net.account.account

Additionally, accounts in Cairo1 are now supported! You can pass additional argument ``cairo_version`` to :meth:`Account.sign_invoke_transaction` method.


0.18.1 Minor changes
--------------------

1. Parameter ``include_block`` in :meth:`GatewayClient.get_state_update` doesn't work on mainnet gateway (an error is thrown).

.. currentmodule:: starknet_py.net.account.account

2. :meth:`Account.sign_invoke_transaction` now accepts additional parameter ``cairo_version``, which allows specifying which type of calldata encoding should be used.

|

.. raw:: html

  <hr>

|


**********************
0.18.0 Migration guide
**********************

This version of starknet.py brings support Starknet 0.12.1, 0.12.2 and `RPC v0.4.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.4.0>`_!


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

5. Lowered ``check_interval`` parameter default value in :meth:`Client.wait_for_tx` from 5 seconds to 2.

.. currentmodule:: starknet_py.net.client_models

6. Added fields to dataclasses that previously were missing (e.g. ``contract_address_salt`` in :class:`DeployTransaction`).

.. currentmodule:: starknet_py.cairo.felt

7. :func:`decode_shortstring` now is returned without ``\x00`` in front of the decoded string.

.. currentmodule:: starknet_py.net.gateway_client

8. Added two new methods to :class:`GatewayClient` - :meth:`GatewayClient.get_public_key` and :meth:`GatewayClient.get_signature`.
9. :meth:`GatewayClient.get_state_update` now accepts additional parameter - `include_block`.

.. currentmodule:: starknet_py.net.signer.stark_curve_signer

10. :class:`KeyPair` and :meth:`KeyPair.from_private_key` now can accept keys in string representation.


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

2. :meth:`Account.sign_invoke_transaction`, :meth:`Account.sign_declare_transaction`, :meth:`Account.sign_declare_v2`, :meth:`Account.sign_deploy_account_transaction` and :meth:`Account.execute` can now accept custom ``nonce`` parameter.
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
10. Changed name of ``starknet_py.transaction_exceptions`` to ``starknet_py.transaction_errors`` to match other files.

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

* Use ``GatewayClient`` to interact with Starknet like you did in previous starknet.py versions
* Use :ref:`FullNodeClient` to interact with JSON-RPC

.. note::

    It is no longer possible to create an instance of ``Client``. Doing so will cause
    errors in runtime.

API Changes
-----------

Client methods has had some of the parameters removed, so it provided uniform interface
for both gateway and rpc methods. Please refer to ``GatewayClient`` and :ref:`FullNodeClient`
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
