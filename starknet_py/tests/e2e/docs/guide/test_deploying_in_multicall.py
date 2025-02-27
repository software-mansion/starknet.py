import pytest


@pytest.mark.asyncio
async def test_deploying_in_multicall(account, map_class_hash, map_abi):
    # pylint: disable=import-outside-toplevel,
    # docs: start
    from starknet_py.contract import Contract
    from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
    from starknet_py.net.udc_deployer.deployer import Deployer

    # First, create Deployer instance. For more details see previous paragraph
    deployer = Deployer()

    # Create contract deployment. We will be deploying the `map` contract
    deploy_call, address = deployer.create_contract_deployment(
        class_hash=map_class_hash
    )
    # docs: end
    # docs: start

    # Address of the `map` contract is known here, so we can create its instance!
    map_contract = Contract(
        address=address, abi=map_abi, provider=account, cairo_version=1
    )

    # And now we can prepare a call
    put_call = map_contract.functions["put"].prepare_invoke_v3(key=10, value=20)

    # After that multicall transaction can be sent
    # Note that `deploy_call` and `put_call` are two regular calls!
    invoke_tx = await account.sign_invoke_v3(
        calls=[deploy_call, put_call],
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )

    resp = await account.client.send_transaction(invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    (value,) = await map_contract.functions["get"].call(key=10)
    # value = 20
    # docs: end

    assert value == 20
