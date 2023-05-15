#!/bin/bash

echo "Running most important tests"
coverage run -m pytest -v --reruns 5 --only-rerun aiohttp.client_exceptions.ClientConnectorError starknet_py --ignore=starknet_py/tests/e2e/docs --ignore=starknet_py/tests/e2e/core --ignore=starknet_py/tests/e2e/contract
coverage run -m pytest -v --reruns 5 --only-rerun aiohttp.client_exceptions.ClientConnectorError starknet_py/tests/e2e/contract/contract_interaction
coverage run -m pytest -v --reruns 5 --only-rerun aiohttp.client_exceptions.ClientConnectorError starknet_py/tests/e2e/contract/contract_functionalities
