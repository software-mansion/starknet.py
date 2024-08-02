Mocking interaction with L1
===========================

Abstract
--------

In order to test interaction with L1 contracts, devnet client provides a way to mock the L1 interaction.
Before taking a look at the examples, please get faimiliar with the `devnet postman docs <https://0xspaceshard.github.io/starknet-devnet-rs/docs/postman>`_ and messaging mechanism:

- `Writing messaging contracts <https://book.cairo-lang.org/ch16-04-L1-L2-messaging.html>`_
- `Mechanism overview <https://docs.starknet.io/architecture-and-concepts/network-architecture/messaging-mechanism/>`_
- `StarkGate example <https://docs.starknet.io/architecture-and-concepts/network-architecture/messaging-mechanism/>`_

L1 network setup
----------------

First of all you should deploy `messaging contract <https://github.com/0xSpaceShard/starknet-devnet-rs/blob/138120b355c44ae60269167b326d1a267f7af0a8/contracts/l1-l2-messaging/solidity/src/MockStarknetMessaging.sol>`_ on ethereum network.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/devnet_utils/test_l1_integration.py
    :language: python
    :dedent: 4


L2 -> L1
--------

Deploying L2 interaction contract
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interaction with L1 is done by sending a message using `send_message_to_l1_syscall` function.
So in order to test this functionality, you need to deploy a contract that has this functionality.
Example contract: `l1_l2.cairo <https://github.com/0xSpaceShard/starknet-devnet-js/blob/5069ec3397f31a408d3df2734ae40d93b42a0f7f/test/data/l1_l2.cairo>`_

.. codesnippet:: ../../starknet_py/tests/e2e/docs/devnet_utils/test_l1_integration.py
    :language: python
    :dedent: 4
    :start-after: docs: messaging-contract-start
    :end-before: docs: messaging-contract-end


Consuming message
^^^^^^^^^^^^^^^^^

After deploying the contract, you need to flush the messages to the L1 network.
And then you can consume the message on the L1 network.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/devnet_utils/test_l1_integration.py
    :language: python
    :dedent: 4
    :start-after: docs: flush-1-start
    :end-before: docs: flush-1-end

L1 -> L2
--------

Sending mock transactions from L1 to L2 does not require L1 node to be running.

.. codesnippet:: ../../starknet_py/tests/e2e/docs/devnet_utils/test_l1_integration.py
    :language: python
    :dedent: 4
    :start-after: docs: send-l2-start
    :end-before: docs: send-l2-end


