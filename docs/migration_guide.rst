0.4.8 Migration guide
=====================

0.4.8 of starknet.py brings fresh changes including a breaking change in contracts' code.
To ensure smooth migration to this version please familiarize yourself with this
migration guide.

Breaking Changes
-----------------------

New Cairo syntax
^^^^^^^^^^^^^^^^^^^^^^^

With the update of `cairo-lang <https://github.com/starkware-libs/cairo-lang>`_ to version ``0.10.0``,
the syntax of contracts written in cairo changes significantly.
You can see the new syntax `here <https://starkware.notion.site/starkware/StarkNet-0-10-0-4ac978234c384a30a195ce4070461257#8bfeb76259234f32b5f42376f0d976b9>`_.

As a result, the **old syntax is no longer supported**.

For the already existent programs to be compatible with the new StarkNet version,
they would have to be migrated using ``cairo-migrate`` command from CLI.

.. code-block::

    > cairo-migrate --help
    usage: cairo-migrate [-h] [-v] [--one_item_per_line] [--no_one_item_per_line] [-i | -c] [--migrate_syntax] [--no_migrate_syntax] [--single_return_functions]
                         [--no_single_return_functions]
                         file [file ...]

    A tool to migrate Cairo code from versions before 0.10.0.

    positional arguments:
      file                  File names

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      --one_item_per_line   Put each list item (e.g., function arguments) in a separate line, if the list doesn't fit into a single line.
      --no_one_item_per_line
                            Don't use one per line formatting (see --one_item_per_line).
      -i                    Edit files inplace.
      -c                    Check files' formats.
      --migrate_syntax      Convert the syntax from Cairo versions before 0.10.0.
      --no_migrate_syntax   Don't convert the syntax. This flag should only be used if the syntax was already migrated.
      --single_return_functions
                            In version 0.10.0 some standard library functions, such as abs(), have changed to return 'felt' instead of '(res: felt)'. This requires syntax
                            changes in the calling functions. For example, 'let (x) = abs(-5)' should change to 'let x = abs(-5)'.
      --no_single_return_functions
                            Don't migrate calls to some single-return functions, such as abs(). See '--single_return_functions'.

Python versions
^^^^^^^^^^^^^^^^^^^^^^^

Following Cairo's technical change of moving from ``python3.7`` to ``python3.9``,
starknet.py has dropped support for version ``python3.7``.

Currently, compatible Python versions are ``python3.8`` and ``python3.9``.

New Transaction version
-----------------------

Cairo 0.10.0 brings new version of the transaction.
The differences:

- ``contract_address`` field is now called ``account_contract_address``
- The field ``entry_point_selector`` is removed
- A nonce field is added

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