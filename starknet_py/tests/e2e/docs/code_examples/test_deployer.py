from starknet_py.net.udc_deployer.deployer import Deployer


def test_init():
    # docs: init_start
    deployer = Deployer()
    # or
    deployer = Deployer(deployer_address=0x123)
    # or
    deployer = Deployer(deployer_address=0x123, account_address=0x321)
    # docs: init_end


def test_create_deployment_call():
    abi = []
    calldata = []
    deployer = Deployer()

    # docs: create_deployment_call_start
    contract_deployment = deployer.create_deployment_call(
        class_hash=0x123, salt=1, abi=abi, calldata=calldata
    )
    # docs: create_deployment_call_end
