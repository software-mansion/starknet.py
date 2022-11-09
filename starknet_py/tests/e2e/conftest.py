@pytest.fixture(scope="module")
def new_full_node_account_client(
    new_address_and_private_key: Tuple[str, str], full_node_client: FullNodeClient
) -> AccountClient:
    """
    Returns a new AccountClient created with FullNodeClient
    """
    address, private_key = new_address_and_private_key

    return create_account_client(
        address, private_key, full_node_client, supported_tx_version=1
    )


def net_to_accounts() -> List[str]:
    accounts = [
        "gateway_account_client",
        "new_gateway_account_client",
    ]
    nets = ["--net=integration", "--net=testnet", "testnet", "integration"]

    if set(nets).isdisjoint(sys.argv):
        accounts.extend(["full_node_account_client", "new_full_node_account_client"])
    return accounts


@pytest.fixture(
    scope="module",
    params=net_to_accounts(),
)
def account_client(request) -> AccountClient:
    """
    This parametrized fixture returns all AccountClients, one by one.
    """
    return request.getfixturevalue(request.param)


def net_to_new_accounts() -> List[str]:
    accounts = [
        "new_gateway_account_client",
    ]
    nets = ["--net=integration", "--net=testnet", "testnet", "integration"]

    if set(nets).isdisjoint(sys.argv):
        accounts.extend(["new_full_node_account_client"])
    return accounts


@pytest.fixture(
    scope="module",
    params=net_to_new_accounts(),
)
def new_account_client(request) -> AccountClient:
    """
    This parametrized fixture returns all new AccountClients, one by one.
    """
    return request.getfixturevalue(request.param)