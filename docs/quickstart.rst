Quickstart
==========

Using Client
------------
``Client`` is a facade for interacting with Starknet. It requires information about used network:

.. code-block:: python

    from starknet.contract import Contract
    from starknet.net.client import Client

    # Using predefined networks - use testnet for playing with Starknet
    testnet_client = Client(NetAddress.testnet)
    mainnet_client = Client(NetAddress.mainnet)

    # Local network
    local_network_client = Client("http://localhost:5000")

    call_result = await testnet_client.get_block("0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943)

The default interface is asynchronous. Although it is the recommended way of using Starknet.py, you can also use a
synchronous version. It might be helpful to play with Starknet directly in python interpreter.

.. code-block:: python

    synchronous_testnet_client = Client.sync(NetAddress.testnet)
    call_result = synchronous_testnet_client.get_block("0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943")

You can see all Client's methods here. TODO

Using Contract
--------------
``Contract`` makes interacting with contracts deployed on Starknet much easier:

.. code-block:: python

    from starknet.contract import Contract
    from starknet.utils.types import NetAddress
    from starknet.net.client import Client

    client = Client(net=NetAddress.testnet)
    key = 1234

    # Create contract from contract's address - Contract will download contract's ABI to know its interface.
    contract = Contract.sync.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", client)

    # All exposed functions are available at contract.functions.
    # Here we invoke a function, creating a new transaction.
    invocation = await contract.functions.set_value.invoke(key, 7)

    # Invocation returns InvocationResult object. It exposes a helper for waiting until transaction is accepted.
    await invocation.wait_for_acceptance()

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions.get_value.call(key)
    # saved = 7 now

Although asynchronous API is recommended, you can also use Contract's synchronous API:

.. code-block:: python

    from starknet.contract import Contract
    from starknet.utils.types import NetAddress
    from starknet.net.client import Client

    key = 1234
    contract = Contract.sync.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client(net=NetAddress.testnet))
    invocation = contract.functions.set_value.invoke(key, 7)
    invocation.wait_for_acceptance()

    (saved,) = contract.functions.get_value.call(key) # 7