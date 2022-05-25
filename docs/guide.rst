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
    from starknet_py.net.networks import TESTNET

    contract = Contract(address=address, abi=abi, client=Client(TESTNET))
    # or
    contract = await Contract.from_address(address, Client(TESTNET))

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
    await invocation.wait_for_acceptance()

    (balance,) = await contract.functions["balanceOf"].call(recipient)

    # You can also use key access, call returns NamedTuple
    result = await contract.functions["balanceOf"].call(recipient)
    balance = result.balance

Signing a single transaction
----------------------------
You can use :obj:`ContractFunction's call <starknet_py.contract.ContractFunction.prepare>` to get calldata's parts and generate a signature from them. Here's a contract inspired by `Starknet's docs <https://www.cairo-lang.org/docs/hello_starknet/user_auth.html>`_:

.. code-block:: text

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
    from starknet_py.net.networks import TESTNET

    contract_address = "0x00178130dd6286a9a0e031e4c73b2bd04ffa92804264a25c1c08c1612559f458"
    private_key = 12345
    public_key = 1628448741648245036800002906075225705100596136133912895015035902954123957052
    value = 340282366920938463463374607431768211583

    contract = await Contract.from_address(contract_address, Client(TESTNET))
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
    from starknet_py.net.networks import TESTNET

    contract = """
    %lang starknet
    %builtins pedersen range_check

    from starkware.cairo.common.cairo_builtins import HashBuiltin

    @storage_var
    func public_key() -> (res: felt):
    end

    @constructor
    func constructor{
            syscall_ptr : felt*,
            pedersen_ptr : HashBuiltin*,
            range_check_ptr
        }(_public_key: felt):
        public_key.write(_public_key)
        return()
    end
    """

    client = Client(TESTNET)

    # Use list for positional arguments
    constructor_args = [123]

    # or use dict for keyword arguments
    constructor_args = {"_public_key": 123}

    # contract as a string
    deployment_result = await Contract.deploy(
        client, compilation_source=contract, constructor_args=constructor_args
    )

    # dict with content - useful for multiple files
    deployment_result = await Contract.deploy(
        client, compilation_source={"contract.cairo": contract}, constructor_args=constructor_args
    )

    # or use already compiled program
    compiled = Path("contract_compiled.json").read_text()
    deployment_result = await Contract.deploy(
        client, compiled_contract=compiled, constructor_args=constructor_args
    )

    # you can wait for transaction to be accepted
    await deployment_result.wait_for_acceptance()

    # but you can access the deployed contract object even if has not been accepted yet
    contract = deployment_result.deployed_contract


Handling client errors
-----------------------
You can use ``starknet.net.client.BadRequest`` to catch errors from invalid requests:

.. code-block:: python

    from starknet_py.net.client import Client, BadRequest
    from starknet_py.net.networks import TESTNET
    try:
        contract_address = 1 # Doesn't exist
        await Contract.from_address(contract_address, Client(TESTNET))
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
   * - named tuple
     - dict or NamedTuple
     - ``{"a": 1, "b": 2, "c" : (3, 4)}``, ``NamedTuple("name", [("a", int), ("b", int), ("c", tuple)])(1, 2, (3, 4))``
     -
   * - struct
     - dict with keys matching struct
     - ``{"key_1": 2, "key_2": (1, 2, 3), "key_3": {"other_struct_key": 13}}``
     - Can nest other types apart from pointers
   * - pointer to felt/felt arrays (requires additional ``parameter_len`` parameter)
     - any iterable containing ints
     - ``[1, 2, 3]``, ``[]``, ``(1, 2, 3)``
     - ``parameter_len`` is filled automatically from value
   * - pointer to struct/struct arrays (requires additional ``parameter_len`` parameter)
     - any iterable containing dicts
     - ``[{"key": 1}, {"key": 2}, {"key": 3}]``, ``[]``, ``({"key": 1}, {"key": 2}, {"key": 3})``
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
   * - named tuple
     - NamedTuple
   * - struct
     - dict with keys matching struct
   * - pointer to felt/felt arrays
     - list of ints
   * - pointer to struct/struct arrays
     - list of dicts
   * - unt256
     - int


Working with shortstrings
-------------------------

To make working with short strings easier we provide some utility functions to translate the felt value received from the contract, into a short string value. A function which translates a string into a felt is also available, but the transformation is done automatically when calling the contract with shortstring in place of felt - they are interchangable.
You can read more about how cairo treats shortstrings in `the documentation <https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals>`_.

Conversion functions and references:

- :obj:`encode_shortstring <starknet_py.cairo.felt.encode_shortstring>`
- :obj:`decode_shortstring <starknet_py.cairo.felt.decode_shortstring>`



StarkNet <> Ethereum communication
----------------------------------

To retrieve the StarkNet -> Ethereum or Ethereum -> StarkNet message count, you need to provide some data that you used to create that message.
Then after creating the message's representation, you can query it's current count.

You can find out more about StarkNet <> Ethereum messaging here: https://starknet.io/documentation/l1-l2-messaging/

Full API description :ref:`here<Messaging>`.



Ethereum -> StarkNet messages
#############################

The message's count is an `int`, representing the number of unconsumed messages on L2 with that exact content.
Since the `nonce`'s value will always be unique for each message, this value is either 0 or 1
(0 meaning the message is consumed or not received yet, and 1 for unconsumed, queued message).

.. code-block:: python

    from starknet_py.net.l1.messages import (
        MessageToStarknetContent,
        MessageToStarknet,
    )
    from starknet_py.net.models import StarknetChainId
    from starknet_py.contract import ContractFunction

        ## All of the construction methods shown below are correct:

        # 1. From message content
        eth_to_sn_msg = MessageToStarknet.from_content(
            MessageToStarknetContent(
                eth_sender=123, # Integer representation of Eth hex address
                starknet_recipient="0x123123123", # Either a hex SN address, or it's integer representation
                nonce=1, # Can be retrieved from Eth transaction's receipt (the one containing the sent message)
                selector=ContractFunction.get_selector("dummy_name"), # SN function selector based on function name
                payload=[32, 32, 32, 32], # SN Function calldata, list of ints
            )
        )

        # 2. From message hash
        eth_to_sn_msg = MessageToStarknet.from_hash(
            (123).to_bytes(32, "big") # Provide 32 bytes as an input here, instead of message's content
        )

        # 3. From Eth transaction receipt (provided by web3.py, like shown below)
        w3 = web3.Web3(web3.providers.HTTPProvider("https://my-rpc-endpoint.com/"))
        tx_receipt = w3.eth.wait_for_transaction_receipt("0x123123123")
        eth_to_sn_msg = MessageToStarknet.from_tx_receipt(tx_receipt)

        # 4. From transaction hash (fetches the receipt for you)
        eth_to_sn_msg = await MessageToStarknet.from_tx_hash( # For sync version, use 'from_tx_hash_sync'
            tx_hash="0x123123123",
            endpoint_uri="https://my-rpc-endpoint.com/", # Only HTTP RPC endpoints are supported for now
        )

        # After message construction, we can fetch queued messages count
        count = eth_to_sn_msg.count_queued_sync(
            chain_id=StarknetChainId.TESTNET,
            endpoint_uri="https://my-rpc-endpoint.com/", # Only HTTP RPC endpoints are supported for now
            block_number="pending" # Block number or block representation literal. Optional parameter
        )


StarkNet -> Ethereum messages
#############################

As in previous section, you can provide L1 message content, and then fetch the queued message count.
The return value is an `int`, representing the number of unconsumed messages on L1 of that exact content.

.. code-block:: python

    from starknet_py.net.l1.messages import (
        MessageToEth,
        MessageToEthContent,
    )
    from starknet_py.net.client import Client
    from starknet_py.net.models import StarknetChainId
    from starknet_py.net.networks import TESTNET

    ## All of the construction methods shown below are correct:

    # 1. From message content
    sn_to_eth_msg = MessageToEth.from_content(
        MessageToEthContent(
            starknet_sender='0x123123123', # Either a hex SN address, or it's integer representation
            eth_recipient=123, # Integer representation of Eth hex address
            payload=[123, 123]
        )
    )

    # 2. From message hash
    sn_to_eth_msg = MessageToEth.from_hash(
        (123).to_bytes(32, "big") # Provide 32 bytes as an input here, instead of message's content
    )

    # 3. From l2 (StarkNet) transaction receipt (provided by starknet.py, like shown below)
    tx_receipt = await Client(TESTNET).get_transaction_receipt("0x123123123")
    sn_to_eth_msg = MessageToEth.from_tx_receipt(tx_receipt)

    # 4. From transaction hash (fetches the receipt for you)
    sn_to_eth_msg = await MessageToEth.from_tx_hash( # For sync version, use 'from_tx_hash_sync'
        "0x123123123", Client(TESTNET)
    )

    # After message construction, we can fetch queued messages count
    count = sn_to_eth_msg.count_queued_sync(
        chain_id=StarknetChainId.TESTNET,
        endpoint_uri="https://my-rpc-endpoint.com/", # Only HTTP RPC endpoints are supported for now
        block_number="pending" # Block number or block representation literal
    )
