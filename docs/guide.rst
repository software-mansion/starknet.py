Guide
=====

Using existing contracts
------------------------

Although it is possible to use :ref:`Client` to interact with contracts, it requires translating python values into Cairo
values. Contract offers that and some other utilities.

Let's say we have a contract with this interface:

.. code-block:: python

    abi = [
        {
            "inputs": [
                {
                    "name": "sender",
                    "type": "felt"
                },
                {
                    "name": "recipient",
                    "type": "felt"
                },
                {
                    "name": "amount",
                    "type": "felt"
                }
            ],
            "name": "transferFrom",
            "outputs": [
                {
                    "name": "success",
                    "type": "felt"
                }
            ],
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "account",
                    "type": "felt"
                }
            ],
            "name": "balanceOf",
            "outputs": [
                {
                    "name": "balance",
                    "type": "felt"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]


This is how we can interact with it:

.. code-block:: python

    from starknet.utils.types import NetAddress
    from starknet.net.client import Client
    from starknet.contract import Contract

    contract = Contract(address=address, abi=abi, client=Client(net=NetAddress.testnet))
    # or
    contract = await Contract.from_address(address, Client(net=NetAddress.testnet))

    # Using only positional arguments
    invocation = await contract.functions.transferFrom.invoke(sender, recipient, 10000)

    # Using only keyword arguments
    invocation = await contract.functions.transferFrom.invoke(sender=sender, recipient=recipient, amount=10000)

    # Mixing positional with keyword arguments
    invocation = await contract.functions.transferFrom.invoke(sender, recipient, amount=10000)

    # Wait for tx
    await invocation.wait_for_acceptance

    (balance,) = await contract.functions.balanceOf.call(recipient)

    # You can also call .to_dict on value returned from a call to get keyed values. It is useful with many returned
    # values.
    result = await contract.functions.balanceOf.call(recipient)
    balance = result.to_dict()["balance"]

Deploying new contracts
-----------------------

Here's how you can deploy new contracts:

.. code-block:: python

    from starknet.net.client import Client
    from starknet.contract import Contract
    from pathlib import Path

    contract = """
    %lang starknet
    %builtins pedersen

    from starkware.cairo.common.cairo_builtins import HashBuiltin

    @storage_var
    func public_key() -> (res: felt):
    end

    @constructor
    func constructor{
            syscall_ptr : felt*,
            pedersen_ptr : HashBuiltin*
        }(public_key: felt):
        public_key.write(public_key)
        return()
    end
    """

    client = Client(net=NetAddress.testnet)

    # Use list for positional arguments
    constructor_args = [123]

    # or use dict for keyword arguments
    constructor_args = {"public_key": 123}

    # contract as a string
    deployed_contract = await Contract.deploy(
        client, compilation_source=contract, constructor_args=constructor_args
    )

    # dict with content - useful for multiple files
    deployed_contract = await Contract.deploy(
        client, compilation_source={"contract.cairo": contract}, constructor_args=constructor_args
    )

    # or use already compiled program
    compiled = Path("contract_compiled.json").read_text()
    deployed_contract = await Contract.deploy(
        client, compiled_contract=compiled, constructor_args=constructor_args
    )


Data transformation
-------------------

Starknet.py transforms python values to Cairo values and the other way around.

.. list-table:: Data transformation of ``parameter`` to Cairo values
   :widths: 25 25 25 25
   :header-rows: 1

   * - Expected Cairo type
     - Accepted python types
     - Example python values
     - Comment
   * - felt
     - int
     - ``0``, ``-1``, ``1213124124``
     -
   * - tuple
     - any iterable of matching size
     - ``(1, 2, (9, 8))``, ``[1, 2, (9, 8)]``, ``(v for v in [1, 2, (9, 8)])``
     - Can nest other types apart from pointers
   * - struct
     - dict with keys matching struct
     - ``{"key_1": 2, "key_2": (1, 2, 3), "key_3": {"other_struct_key": 13}}``
     - Can nest other types apart from pointers
   * - pointer to felt/felt arrays (requires additional ``parameter_len`` parameter)
     - any iterable containing ints
     - ``[1, 2, 3]``, ``[]``, ``(1, 2, 3)``
     - ``parameter_len`` is filled automatically from value



.. list-table:: Data transformation of ``parameter`` from Cairo values
   :widths: 25 25
   :header-rows: 1

   * - Cairo type
     - Python type
   * - felt
     - int
   * - tuple
     - tuple
   * - struct
     - dict with keys matching struct
   * - pointer to felt/felt arrays
     - list of ints
