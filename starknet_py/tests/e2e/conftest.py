@pytest_asyncio.fixture(scope="module")
async def deployer_address(gateway_client: AccountClient) -> int:
    """
    Returns an address of the UDC
    """
    deploy_tx = make_deploy_tx(
        compilation_source=(contracts_dir / "universal_deployer.cairo").read_text(
            "utf-8"
        )
    )
    res = await gateway_client.deploy(deploy_tx)
    return res.contract_address


@pytest_asyncio.fixture(scope="module")
async def map_class_hash(
    new_gateway_account_client: AccountClient, map_source_code: str
) -> int:
    """
    Returns class_hash of the map.cairo
    """
    declare = await new_gateway_account_client.sign_declare_transaction(
        compilation_source=map_source_code,
        max_fee=int(1e16),
    )
    res = await new_gateway_account_client.declare(declare)
    await new_gateway_account_client.wait_for_tx(res.transaction_hash)
    return res.class_hash


constructor_with_arguments_source = (
    contracts_dir / "constructor_with_arguments.cairo"
).read_text("utf-8")


@pytest.fixture(scope="module")
def constructor_with_arguments_abi() -> List:
    """
    Returns an abi of the constructor_with_arguments.cairo
    """
    compiled_contract = create_compiled_contract(
        compilation_source=constructor_with_arguments_source
    )
    return compiled_contract.abi


@pytest_asyncio.fixture(scope="module")
async def constructor_with_arguments_class_hash(
    new_gateway_account_client: AccountClient,
) -> int:
    """
    Returns a class_hash of the constructor_with_arguments.cairo
    """
    declare = await new_gateway_account_client.sign_declare_transaction(
        compilation_source=constructor_with_arguments_source,
        max_fee=int(1e16),
    )
    res = await new_gateway_account_client.declare(declare)
    await new_gateway_account_client.wait_for_tx(res.transaction_hash)
    return res.class_hash