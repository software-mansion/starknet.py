# pylint: disable=unused-variable
from starknet_py.net.udc_deployer.deployer import Deployer


def test_init():
    # docs-start: init
    deployer = Deployer()
    # or
    deployer = Deployer(deployer_address=0x123)
    # or
    deployer = Deployer(deployer_address=0x123, account_address=0x321)
    # docs-end: init


def test_create_deployment_call_raw():
    deployer = Deployer()

    # docs-start: create_deployment_call_raw
    contract_deployment = deployer.create_deployment_call_raw(
        class_hash=0x123, salt=1, raw_calldata=[3, 1, 2, 3]
    )
    # docs-end: create_deployment_call_raw
