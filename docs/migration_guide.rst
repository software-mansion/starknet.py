0.5.0 Migration guide
=====================

``cairo-lang`` 0.10.0 brings a lot of new exciting changes, like:

- new cairo syntax,
- new transaction version (1),
- new ``__validate__`` endpoint in accounts.

``starknet.py`` 0.5.0 has an experimental support for new features and tries to minimize number of breaking changes for
users who want to use the old transaction version (0). Please note that support for this transaction version will be
removed in the future.

Breaking Changes
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

Python versions
^^^^^^^^^^^^^^^^^^^^^^^

We drop support for python 3.7.X, following `cairo-lang` support. You must use python 3.8+ to use starknet.py 0.5.0.

InvokeFunction and Declare
^^^^^^^^^^^^^^^^^^^^^^^

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

    In the future versions default value of ``supported_tx_version`` will be changed to 1. This will happen when the old account is deprecated.


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