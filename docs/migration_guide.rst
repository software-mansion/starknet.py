0.11.0 Migration guide
======================

Cairo-lang 0.10.3 dropped support for the `Deploy` transaction. To be compatible we had to remove some
(already deprecated) features.

Breaking Changes
----------------

Methods below are removed:
- deprecated `Contract.deploy`. Read more about deployment in the
`Deploying contracts <https://starknetpy.readthedocs.io/en/latest/guide.html#deploying-contracts>`_ section.
- deprecated `AccountClient.create_account`. `Account creation <https://starknetpy.readthedocs.io/en/latest/account_creation.html>`_
docs are here to help you!
- `Client.deploy` method (from the interface and all implementations)
- deprecated `make_deploy_tx`
- `compute_deploy_hash`
- the `Deploy` transaction


0.9.0 Migration guide
=====================

Starknet.py 0.9.0 brings support for `RPC 0.2.0 <https://github.com/starkware-libs/starknet-specs/releases/tag/v0.2.0>`_,
updates :meth:`Contract.from_address` method to work with the newest proxies and removes some deprecated features.

0.9.0 Breaking Changes
----------------------

- Removed deprecated `Account.sign_transaction`. Use new `Account.sign_invoke_transaction`.
- Removed deprecated `InvokeFunction` as `call_contract` parameter. Use `Call` class instead.
- `StateDiff` has `declared_contract_hashes` instead of `declared_contracts` field (only name has changed).
- Support for RPC 0.1.0 has been dropped in favour of RPC 0.2.0.


Contract.from_address
---------------------

Check out the Guide with the new section :ref:`Resolving proxies` to see how to easily use proxies with the Starknet.py.


0.8.0 Migration guide
=====================

Cairo-lang 0.10.1 brings support for `DEPLOY_ACCOUNT` transactions that will completely
replace currently used `DEPLOY` transactions sometime in the future.

You should already modify your applications to use new deployment flow to either support deployments
using new flow:

1. Declare a contract on starknet using `Declare` transaction
2. Pre-fund the address of new account with enough tokens to cover transaction costs
3. Send a `DeployAccount` transaction with the pre-funded address

or support deploying through syscall or `Universal Deployer Contract <https://community.starknet.io/t/universal-deployer-contract-proposal/1864>`_.

0.8.0 Breaking Changes
----------------------

- `entry_point_selector` has been removed from `v1` transactions. `InvokeTransaction`'s field has been changed to `Optional[int]`
- `net.models.address.compute_address` signature has been changed and use of keyword arguments is now mandatory
- `Client.estimate_fee` ABC now also accepts `DeployAccount` transaction as `tx` parameter. Custom clients should be updated to reflect this change.


Deprecations
------------

- `Contract.deploy` has been deprecated in favor of new `DeployAccount` flow
- `Client.deploy` has been deprecated

0.5.0 Migration guide
=====================

``cairo-lang`` 0.10.0 brings a lot of new exciting changes, like:

- new cairo syntax,
- new transaction version (1),
- new ``__validate__`` endpoint in accounts.

``starknet.py`` 0.5.0 has an experimental support for new features and tries to minimize number of breaking changes for
users who want to use the old transaction version (0). Please note that support for this transaction version will be
removed in the future.

.. note::

    There is no need to upgrade ``starknet.py`` to the newest version because the old one is still compatible with StarkNet.
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


For the already existent programs to be compatible with the new StarkNet version,
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

``make_declare_tx`` is deprecated, because in the future versions of StarkNet unsigned declare transactions will not be
supported. :meth:`~starknet_py.net.account.account_client.AccountClient.sign_declare_transaction` should be used to create
and sign declare transaction.

Deploy transaction
^^^^^^^^^^^^^^^^^^

Deploy transactions will not be supported in the future versions of StarkNet, so ``make_deploy_tx`` is deprecated.
Contracts should be deployed through cairo syscall.

0.4.0 Migration guide
=====================

0.4.0 of starknet.py brings multiple changes including breaking changes to API.
To ensure smooth migration to this version please familiarize yourself with this
migration guide.

Overlook of the changes
-----------------------

0.4.0 brings support for the `starknet rpc interface <https://github.com/starkware-libs/starknet-specs/blob/606c21e06be92ea1543fd0134b7f98df622c2fbf/api/starknet_api_openrpc.json>`_.

This required us to introduce some big changes to the clients. API methods has
remained mostly the same, but their parameters changed. Also, we've introduced custom dataclasses
for every endpoint, that are simplified from these from ``cairo-lang`` library.

This provides uniform interface for both starknet gateway (only supported way of interacting with
starknet in previous StarkNet.py versions), as well as JSON-RPC.

Clients
-------

Client has been separated into two specialized modules.

* Use :ref:`GatewayClient` to interact with StarkNet like you did in previous starknet.py versions
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
Instead they require a prepared transactions. These can be created using :ref:`Transactions` module

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
now prepare and send transactions to StarkNet.

Contract changes
----------------

Transaction's status is not checked while invoking through Contract interface, because RPC write API doesn't return "code"
parameter. To check if the transaction passed use wait_for_acceptance on InvokeResult.