# This is needed for importing fixtures from `fixtures` directory
pytest_plugins = [
    "starknet_py.tests.e2e.client.fixtures.transactions",
    "starknet_py.tests.e2e.fixtures.clients",
    "starknet_py.tests.e2e.fixtures.account_clients",
    "starknet_py.tests.e2e.fixtures.contracts",
    "starknet_py.tests.e2e.client.fixtures.prepare_network",
    "starknet_py.tests.e2e.fixtures.utils",
]
