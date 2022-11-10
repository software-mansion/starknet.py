import pytest
from starkware.starknet.public.abi import get_selector_from_name


@pytest.mark.asyncio
async def test_using_cairo_serializer(network, gateway_account_client):
    # pylint: disable=unused-variable, too-many-locals, import-outside-toplevel
    # docs: start
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.models import StarknetChainId
    from starknet_py.contract import Contract
    from starknet_py.net import AccountClient
    from starknet_py.utils.data_transformer.data_transformer import CairoSerializer

    # Code of the contract which emits an event
    contract = """
        %lang starknet
        %builtins pedersen range_check
        
        from starkware.cairo.common.cairo_builtins import HashBuiltin
        
        @storage_var
        func storage(key: felt) -> (value: felt) {
        }
        
        @event
        func put_called(key: felt, prev_value: felt, value: felt) {
        }
        
        @external
        func put{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(key: felt, value: felt) {
            let (prev_value) = storage.read(key);
            put_called.emit(key=key, prev_value=prev_value, value=value);
            storage.write(key, value);
            return ();
        }
    """

    net = "testnet"  # Can be "mainnet" or other custom net too
    # docs: end

    net = network
    # docs: start

    # Creates an account
    client = await AccountClient.create_account(
        client=GatewayClient(net=net),
        chain=StarknetChainId.TESTNET,
    )
    # docs: end

    client = gateway_account_client
    # docs: start

    # Deploys the contract
    deployment_result = await Contract.deploy(client, compilation_source=contract)
    await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    # Invokes "put" function (which emits an event)
    invoke_result = (
        await contract.functions["put"].prepare(10, 20, max_fee=int(1e16)).invoke()
    )
    await invoke_result.wait_for_acceptance()

    transaction_hash = invoke_result.hash
    transaction_receipt = await client.get_transaction_receipt(transaction_hash)

    # Takes events from transaction receipt
    events = transaction_receipt.events

    # Takes an abi of the event which data we want to serialize
    emitted_event_abi = {
        "data": [
            {"name": "key", "type": "felt"},
            {"name": "prev_value", "type": "felt"},
            {"name": "value", "type": "felt"},
        ],
        "keys": [],
        "name": "put_called",
        "type": "event",
    }

    # Creates CairoSerializer with contract's identifier manager
    cairo_serializer = CairoSerializer(
        identifier_manager=contract.data.identifier_manager
    )

    # Transforms cairo data to python (needs types of the values and values)
    python_data = cairo_serializer.to_python(
        value_types=emitted_event_abi["data"], values=events[0].data
    )

    # Transforms python data to cairo (needs types of the values and python data)
    cairo_data = cairo_serializer.from_python(emitted_event_abi["data"], *python_data)

    # Function's data can be serialized in the same way
    # docs: end

    assert events[0].from_address == contract.address
    assert events[0].keys[0] == get_selector_from_name("put_called")
