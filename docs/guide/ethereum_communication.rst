StarkNet <> Ethereum communication
==================================

.. warning::
    StarkNet <> Ethereum Messaging module is deprecated. If you are using it,
    please contact us on our StarkNet discord channel: starknet-py.

To retrieve the StarkNet -> Ethereum or Ethereum -> StarkNet message count, you need to provide some data that you used to create that message.
Then after creating the message's representation, you can query its current count.

You can find out more about StarkNet <> Ethereum messaging here: https://starknet.io/documentation/l1-l2-messaging/

Full API description :ref:`here<Messaging>`.



Ethereum -> StarkNet messages
#############################

The message's count is an `int`, representing the number of unconsumed messages on L2 with that exact content.
Since the `nonce`'s value will always be unique for each message, this value is either 0 or 1
(0 meaning the message is consumed or not received yet, and 1 for unconsumed, queued message).

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_eth_sn_messages.py
    :language: python
    :dedent: 4


StarkNet -> Ethereum messages
#############################

As in previous section, you can provide L1 message content, and then fetch the queued message count.
The return value is an `int`, representing the number of unconsumed messages on L1 of that exact content.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_sn_eth_messages.py
    :language: python
    :dedent: 4
