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

    from starknet_py.net.client import Client
    from starknet_py.contract import Contract

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
You can use :obj:`ContractFunction's call <starknet_py.contract.ContractFunction.prepare>` to get calldata's parts and generate a signature from them. Here's a contract inspired by `Starknet's docs <https://www.cairo-lang.org/docs/hello_starknet/user_auth.html>`_:

.. code-block:: cairo

    %lang starknet

    %builtins pedersen range_check ecdsa

    from starkware.cairo.common.uint256 import Uint256
    from starkware.cairo.common.cairo_builtins import (HashBuiltin, SignatureBuiltin)
    from starkware.cairo.common.hash import hash2
    from starkware.cairo.common.signature import (verify_ecdsa_signature)
    from starkware.starknet.common.syscalls import get_tx_signature

    @storage_var
    func balance(user) -> (res: Uint256):
    end

    @external
    func set_balance{
            syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
            range_check_ptr, ecdsa_ptr : SignatureBuiltin*}(
            user : felt, amount : Uint256):
        let (sig_len : felt, sig : felt*) = get_tx_signature()

        # Verify the signature length.
        assert sig_len = 2

        let (hash) = hash2{hash_ptr=pedersen_ptr}(amount.low, 0)
        let (amount_hash) = hash2{hash_ptr=pedersen_ptr}(amount.high, hash)

        # Verify the user's signature.
        verify_ecdsa_signature(
            message=amount_hash,
            public_key=user,
            signature_r=sig[0],
            signature_s=sig[1])

        balance.write(user, amount)
        return ()
    end

    @external
    func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(user : felt) -> (balance: Uint256):
        let (value) = balance.read(user=user)
        return (value)
    end

Here's how you could sign an invocation:

.. code-block:: python

    from starknet_py.utils.crypto.facade import sign_calldata
    from starknet_py.contract import Contract
    from starknet_py.net.client import Client

    contract_address = "0x00178130dd6286a9a0e031e4c73b2bd04ffa92804264a25c1c08c1612559f458"
    private_key = 12345
    public_key = 1628448741648245036800002906075225705100596136133912895015035902954123957052
    value = 340282366920938463463374607431768211583

    contract = await Contract.from_address(contract_address, Client("testnet"))
    prepared = contract.functions["set_balance"].prepare(user=public_key, amount=value)
    # Every transformed argument is stored in prepared.arguments
    # prepared.arguments = {"public_key": public_key, "amount": [127, 1]}

    signature = sign_calldata(prepared.arguments["amount"], private_key)
    invocation = await prepared.invoke(signature)
    await invocation.wait_for_acceptance()

    (stored,) = await contract.functions["get_balance"].call(public_key)
    assert stored == value


Deploying new contracts
-----------------------

Here's how you can deploy new contracts:

.. code-block:: python

    from starknet_py.net.client import Client
    from starknet_py.contract import Contract
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


Handling client errors
-----------------------
You can use ``starknet.net.client.BadRequest`` to catch errors from invalid requests:

.. code-block:: python

    from starknet_py.net.client import Client, BadRequest
    try:
        contract_address = 1 # Doesn't exist
        await Contract.from_address(contract_address, Client("testnet"))
    except BadRequest as e:
        print(e.status_code, e.text)


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
     - int, string (at most 31 characters)
     - ``0``, ``1``, ``1213124124``, 'shortstring', ''
     - Provided int must be in range [0;P) - P being the Prime used in cairo-vm.
       Can also be provided a short 31 character string, which will get
       translated into felt with first letter as MSB of the felt
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
   * - uint256
     - int or dict with ``"low"`` and ``"high"`` keys and ints as values
     - ``0``, ``340282366920938463463374607431768211583``, ``{"low": 12, "high": 13}``
     -



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
   * - unt256
     - int


Working with shortstrings
-------------------------

To make working with short strings easier we provide some utility functions to translate the felt value received from the contract, into a short string value. A function which translates a string into a felt is also available, but the transformation is done automatically when calling the contract with shortstring in place of felt - they are interchangable.
You can read more about how cairo treats shortstrings in `the documentation <https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals>`_.

Conversion functions and references:

- :obj:`encode_shortstring <starknet_py.cairo.felt.encode_shortstring>`
- :obj:`decode_shortstring <starknet_py.cairo.felt.decode_shortstring>`



L1 <> L2 messaging
------------------

To retrieve the L1 -> L2 or L2 -> L1 message status, you need to provide some data that you used to create that message.
Then after creating the message's representation, you can query it's status.



L1 -> L2 messages
#################

The message's status is an `int`, representing the number of unconsumed messages on L2 with that exact content.
Since the `nonce`'s value will always be unique for each message, this value is either 0 or 1
(0 meaning the message is consumed or not received yet, and 1 for unconsumed, queued message).

.. code-block:: python

    from starknet_py.net.l1.messages import (
        L2Message,
        L2MessageContent,
    )
    from starknet_py.net.models import StarknetChainId

    l1_to_l2_msg = L2Message.from_content(
            L2MessageContent(
                l1_sender=123, # Integer representation of L1 hex address
                l2_recipient="0x123123123", # Either a hex L2 address, or it's integer representation
                nonce=1, # Can be retrieved from L1 transaction's receipt (the one containing the sent message)
                function_name="dummy_name", # L2 recipient function name
                payload=[32, 32, 32, 32], # L2 Function calldata, list of ints
            )
        )
        status = await l1_to_l2_msg.get_status(  # For sync version, use 'get_status_sync'
            chain_id=StarknetChainId.TESTNET,
            endpoint_uri="https://my-rpc-endpoint.com/", # Only HTTP RPC endpoints are supported for now
            block_number="pending" # Block number or block representation literal. Optional parameter
        )

The alternative would be providing just the hash of the message (if you have it calculated), instead of message's content:

.. code-block:: python

    from starknet_py.net.l1.messages import (
        L2Message,
        L2MessageContent,
    )
    from starknet_py.net.models import StarknetChainId

    l1_to_l2_msg = L2Message.from_hash(
        (123).to_bytes(32, "big") # Provide 32 bytes as an input here, instead of message's content
    )

    status = await l1_to_l2_msg.get_status(  # For sync version, use 'get_status_sync'
        chain_id=StarknetChainId.TESTNET,
        endpoint_uri="https://my-rpc-endpoint.com/", # Only HTTP RPC endpoints are supported for now
        block_number="pending" # Block number or block representation literal. Optional parameter
    )


L2 -> L1 messages
#################

As in previous section, you can provide L1 message content, and then fetch the status.
The status is an `int`, representing the number of unconsumed messages on L1 of that exact content.

.. code-block:: python

    from starknet_py.net.l1.messages import (
        L2Message,
        L2MessageContent,
    )
    from starknet_py.net.models import StarknetChainId

    l2_to_l1_msg = await L1Message.from_content(
        L1MessageContent(
            l2_sender='0x123123123', # Either a hex L2 address, or it's integer representation
            l1_recipient=123, # Integer representation of L1 hex address
            payload=[123, 123]
        )
    )

    status = await l2_to_l1_msg.get_status(  # For sync version, use 'get_status_sync'
        chain_id=StarknetChainId.TESTNET,
        endpoint_uri="https://my-rpc-endpoint.com/", # Only HTTP RPC endpoints are supported for now
        block_number="pending" # Block number or block representation literal
    )

Providing the hash is also possible (32 bytes):

.. code-block:: python

    from starknet_py.net.l1.messages import (
        L2Message,
        L2MessageContent,
    )
    from starknet_py.net.models import StarknetChainId

    l2_to_l1_msg = await L2Message.from_hash(
        (123).to_bytes(32, "big") # Provide 32 bytes as an input here, instead of message's content
    )

    status = await l2_to_l1_msg.get_status(  # For sync version, use 'get_status_sync'
        chain_id=StarknetChainId.TESTNET,
        endpoint_uri="https://my-rpc-endpoint.com/", # Only HTTP RPC endpoints are supported for now
        block_number="pending" # Block number or block representation literal
    )