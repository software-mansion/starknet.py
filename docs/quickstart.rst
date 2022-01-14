Quickstart
==========

Using Client
------------
:obj:`Client <starknet_py.net.Client>` is a facade for interacting with Starknet. It requires information about used network:

.. code-block:: python

    from starknet_py.contract import Contract
    from starknet_py.net.client import Client

    # Use testnet for playing with Starknet
    testnet_client = Client("https://alpha4.starknet.io")
    mainnet_client = Client("https://alpha-mainnet.starknet.io")

    # Local network
    from starknet_py.net.models import StarknetChainId
    local_network_client = Client("http://localhost:5000", chain=StarknetChainId.TESTNET)

    call_result = await testnet_client.get_block("0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943)

The default interface is asynchronous. Although it is the recommended way of using Starknet.py, you can also use a
synchronous version. It might be helpful to play with Starknet directly in python interpreter.

.. code-block:: python

    synchronous_testnet_client = Client("testnet")
    call_result = synchronous_testnet_client.get_block_sync("0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943")

You can see all Client's methods :obj:`here <starknet_py.net.Client>`.

Using AccountClient
-------------------

:obj:`AccountClient <starknet_py.net.account.account_client.AccountClient>` is an extension of a regular :obj:`Client <starknet_py.net.Client>`. It leverages `OpenZeppelin's Cairo contracts <https://github.com/OpenZeppelin/cairo-contracts>`_ to create an account contract which proxies (and signs) the calls to other contracts on Starknet.

Example usage:

.. code-block:: python

    # Creates an account on local network and returns an instance
    acc_client = await AccountClient.create_account(net="testnet")

    # Deploy an example contract which implements a simple k-v store. Deploy transaction is not being signed.
    map_contract = await Contract.deploy(
        client=acc_client, compilation_source=map_source_code
    )
    k, v = 13, 4324
    # Adds a transaction to mutate the state of k-v store. The call goes through account proxy, because we've used AccountClient to create the contract object
    await map_contract.functions["put"].invoke(k, v)
    (resp,) = await map_contract.functions["get"].call(k) # Retrieves the value, which is equal to 4324 in this case

Using Contract
--------------
:obj:`Contract <starknet_py.contract.Contract>` makes interacting with contracts deployed on Starknet much easier:

.. code-block:: python

    from starknet_py.contract import Contract
    from starknet_py.net.client import Client

    client = Client("testnet")
    key = 1234

    # Create contract from contract's address - Contract will download contract's ABI to know its interface.
    contract = Contract.sync.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", client)

    # All exposed functions are available at contract.functions.
    # Here we invoke a function, creating a new transaction.
    invocation = await contract.functions["set_value"].invoke(key, 7)

    # Invocation returns InvocationResult object. It exposes a helper for waiting until transaction is accepted.
    await invocation.wait_for_acceptance()

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["get_value"].call(key)
    # saved = 7 now

Although asynchronous API is recommended, you can also use Contract's synchronous API:

.. code-block:: python

    from starknet_py.contract import Contract
    from starknet_py.net.client import Client

    key = 1234
    contract = Contract.from_address_sync("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client("testnet"))
    invocation = contract.functions["set_value"].invoke_sync(key, 7)
    invocation.wait_for_acceptance_sync()

    (saved,) = contract.functions["get_value"].call_sync(key) # 7