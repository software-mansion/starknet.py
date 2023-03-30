import pytest

from starknet_py.net.client_models import CasmClass
from starknet_py.net.udc_deployer.deployer import _get_random_salt
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test_cairo1_contract(
    gateway_account, sierra_minimal_compiled_contract_and_class_hash, gateway_client
):
    # pylint: disable=import-outside-toplevel, too-many-locals
    # TODO: use account when RPC 0.3.0 is supported
    account = gateway_account
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash

    contract_compiled_casm = read_contract("precompiled/minimal_contract_compiled.casm")

    # docs: start
    from starknet_py.hash.casm_class_hash import compute_casm_class_hash
    from starknet_py.net.schemas.gateway import CasmClassSchema

    # contract_compiled_casm is the output of the starknet-sierra-compile (.casm file)
    casm_class = CasmClassSchema().loads(contract_compiled_casm)

    # Compute Casm class hash
    casm_class_hash = compute_casm_class_hash(casm_class)
    # docs: end

    assert casm_class_hash == compiled_class_hash

    # docs: start

    # Create Declare v2 transaction
    declare_v2_transaction = await account.sign_declare_v2_transaction(
        # compiled_contract is the output of the starknet-compile (.json file)
        compiled_contract=compiled_contract,
        compiled_class_hash=casm_class_hash,
        max_fee=MAX_FEE,
    )

    # Send Declare v2 transaction
    resp = await account.client.declare(transaction=declare_v2_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    sierra_class_hash = resp.class_hash
    # docs: end

    assert sierra_class_hash != 0

    # START OF DEPLOY SECTION
    raw_calldata = []
    salt = _get_random_salt()
    # docs-deploy: start
    from starknet_py.net.udc_deployer.deployer import Deployer

    # Use Universal Deployer Contract (UDC) to deploy the Cairo1 contract
    deployer = Deployer()

    # Create a ContractDeployment, optionally passing salt and raw_calldata
    contract_deployment = deployer.create_contract_deployment_raw(
        class_hash=sierra_class_hash, raw_calldata=raw_calldata, salt=salt
    )

    # Using the call, create an Invoke transaction to the UDC
    deploy_invoke_transaction = await account.sign_invoke_transaction(
        calls=contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    # The contract has been deployed and can be found at contract_deployment.address
    # docs-deploy: end

    assert isinstance(contract_deployment.address, int)
    assert contract_deployment.address != 0

    compiled_class = await gateway_client.get_compiled_class_by_class_hash(
        sierra_class_hash
    )
    assert isinstance(compiled_class, CasmClass)
