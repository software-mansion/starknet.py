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

    from starknet.net.client import Client
    from starknet.contract import Contract

    contract = Contract(address=address, abi=abi, client=Client("testnet"))
    # or
    contract = await Contract.from_address(address, Client("testnet"))

    # Using only positional arguments
    invocation = await contract.functions["transferFrom"].invoke(sender, recipient, 10000)

    # Using only keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(sender=sender, recipient=recipient, amount=10000)

    # Mixing positional with keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(sender, recipient, amount=10000)

    # Creating a PreparedFunctionCall - creates a function call with arguments - useful for signing transactions and specifying additional options
    transfer = contract.functions["transferFrom"].prepare(sender, recipient, amount=10000)
    await transfer.invoke()

    # Wait for tx
    await invocation.wait_for_acceptance

    (balance,) = await contract.functions["balanceOf"].call(recipient)

    # You can also use key access, call returns NamedTuple
    result = await contract.functions["balanceOf"].call(recipient)
    balance = result.balance

Signing a single transaction
----------------------------
You can use :obj:`ContractFunction's call <starknet.contract.ContractFunction.prepare>` to get calldata's parts and generate a signature from them. Here's an example function
copied from `Starknet's docs <https://www.cairo-lang.org/docs/hello_starknet/user_auth.html>`_:

.. code-block:: cairo

    # Increases the balance of the given user by the given amount.
    @external
    func increase_balance{
            syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
            range_check_ptr, ecdsa_ptr : SignatureBuiltin*}(
            user : felt, amount : felt):
        # Fetch the signature.
        let (sig_len : felt, sig : felt*) = get_tx_signature()

        # Verify the signature length.
        assert sig_len = 2

        # Compute the hash of the message.
        # The hash of (x, 0) is equivalent to the hash of (x).
        let (amount_hash) = hash2{hash_ptr=pedersen_ptr}(amount, 0)

        # Verify the user's signature.
        verify_ecdsa_signature(
            message=amount_hash,
            public_key=user,
            signature_r=sig[0],
            signature_s=sig[1])

        let (res) = balance.read(user=user)
        balance.write(user, res + amount)
        return ()
    end

Here's how you could sign an invocation:

.. code-block:: python

    from starknet.utils.crypto.facade import sign_calldata

    private_key = 12345
    public_key = 1628448741648245036800002906075225705100596136133912895015035902954123957052
    value = 4321

    prepared = contract.functions["increase_balance"].prepare(user=public_key, amount=value)
    # Every transformed argument is stored in prepared.arguments. In this case the translation is easy, but with nested structs it might not be obvious.
    prepared.arguments == {"public_key": public_key, "amount": value}
    signature = sign_calldata(prepared.arguments["amount"], private_key)
    await prepared.invoke(signature)


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

    client = Client("testnet")

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
