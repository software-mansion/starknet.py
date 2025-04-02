Websockets
==========

Abstract
--------
Apart from interacting with Starknet by request-response model, you can also rely on real-time notifications.
Here comes :class:`~starknet_py.net.websockets.websocket_client.WebsocketClient` which allows to establish a connection with Starknet node and listen for events.

Connecting
----------

To begin interacting with Starknet via websockets, create a new instance of :class:`~starknet_py.net.websockets.websocket_client.WebsocketClient` and connect to the node.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/test_websocket_client.py
    :language: python
    :dedent: 4
    :start-after: docs-start: connect
    :end-before: docs-end: connect

Different subscription methods
------------------------------

New block headers
#################

To subscribe to new block headers, use :meth:`~starknet_py.net.websockets.websocket_client.WebsocketClient.subscribe_new_heads`.
Every time a new block is created, the event will be fired.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/test_websocket_client.py
    :language: python
    :dedent: 4
    :start-after: docs-start: subscribe_new_heads
    :end-before: docs-end: subscribe_new_heads

New events
##########

To subscribe to new events, use :meth:`~starknet_py.net.websockets.websocket_client.WebsocketClient.subscribe_events`.
Every time a new event is emitted, the event will be fired.

It's possible to filter events by contract addresses, keys and block id. See all options in the method documentation.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/test_websocket_client.py
    :language: python
    :dedent: 4
    :start-after: docs-start: subscribe_events
    :end-before: docs-end: subscribe_events


Transaction status
##################

To subscribe to transaction status changes, use :meth:`~starknet_py.net.websockets.websocket_client.WebsocketClient.subscribe_transaction_status`.
Every time a transaction status changes, the event will be fired.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/test_websocket_client.py
    :language: python
    :dedent: 4
    :start-after: docs-start: subscribe_transaction_status
    :end-before: docs-end: subscribe_transaction_status


Pending transactions
####################

To subscribe to pending transactions, use :meth:`~starknet_py.net.websockets.websocket_client.WebsocketClient.subscribe_pending_transactions`.
Every time a new pending transaction is added, the event will be fired.

It's possible to filter pending transactions by sender address.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/test_websocket_client.py
    :language: python
    :dedent: 4
    :start-after: docs-start: subscribe_pending_transactions
    :end-before: docs-end: subscribe_pending_transactions

Handling chain reorganization notifications
###########################################

When subscribing to new block headers, events or transactions status, you automatically receive notifications about chain reorganization.
To handle them, you need to set the ``on_chain_reorg`` to your custom function.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/test_websocket_client.py
    :language: python
    :dedent: 4
    :start-after: docs-start: on_chain_reorg
    :end-before: docs-end: on_chain_reorg

Disconnecting
-------------

To disconnect from the node, use :meth:`~starknet_py.net.websockets.websocket_client.WebsocketClient.disconnect`.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/code_examples/test_websocket_client.py
    :language: python
    :dedent: 4
    :start-after: docs-start: disconnect
    :end-before: docs-end: disconnect