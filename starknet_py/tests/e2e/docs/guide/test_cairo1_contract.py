import json

import pytest

from starknet_py.net.client_models import SierraContractClass
from starknet_py.net.udc_deployer.deployer import _get_random_salt
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.fixtures.misc import load_contract


@pytest.mark.asyncio
async def test_cairo1_contract(
    account, sierra_minimal_compiled_contract_and_class_hash
):
    # pylint: disable=too-many-locals
    # pylint: disable=import-outside-toplevel
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash

    contract_compiled_casm = load_contract(
        "MinimalContract",
    )["casm"]

    # docs: start
    from starknet_py.common import create_casm_class
    from starknet_py.hash.casm_class_hash import compute_casm_class_hash

    # contract_compiled_casm is a string containing the content of the starknet-sierra-compile (.casm file)
    casm_class = create_casm_class(contract_compiled_casm)

    # Compute Casm class hash
    casm_class_hash = compute_casm_class_hash(casm_class)
    # docs: end

    assert casm_class_hash == compiled_class_hash

    # docs: start

    # Create Declare v3 transaction
    declare_v3_transaction = await account.sign_declare_v3(
        # compiled_contract is a string containing the content of the starknet-compile (.json file)
        compiled_contract=compiled_contract,
        compiled_class_hash=casm_class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    # Send transaction
    resp = await account.client.declare(transaction=declare_v3_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    sierra_class_hash = resp.class_hash
    # docs: end

    assert sierra_class_hash != 0

    # START OF DEPLOY SECTION
    calldata = []
    salt = _get_random_salt()
    abi = json.loads(compiled_contract)["abi"]
    # docs-deploy: start
    from starknet_py.net.udc_deployer.deployer import Deployer

    # Use Universal Deployer Contract (UDC) to deploy the Cairo1 contract
    deployer = Deployer()

    # Create a ContractDeployment, optionally passing salt and calldata
    contract_deployment = deployer.create_contract_deployment(
        class_hash=sierra_class_hash,
        abi=abi,
        cairo_version=1,
        calldata=calldata,
        salt=salt,
    )

    res = await account.execute_v3(
        calls=contract_deployment.call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await account.client.wait_for_tx(res.transaction_hash)

    # The contract has been deployed and can be found at contract_deployment.address
    # docs-deploy: end

    assert isinstance(contract_deployment.address, int)
    assert contract_deployment.address != 0

    compiled_class = await account.client.get_class_by_hash(
        class_hash=sierra_class_hash
    )
    assert isinstance(compiled_class, SierraContractClass)
