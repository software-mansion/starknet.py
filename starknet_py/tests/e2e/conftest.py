@dataclass
class AccountToBeDeployedDetailsFactory:

    class_hash: int
    fee_contract: Contract

    async def get(self) -> AccountToBeDeployedDetails:
        return await get_deploy_account_details(
            class_hash=self.class_hash, fee_contract=self.fee_contract
        )


@pytest_asyncio.fixture(scope="module")
async def deploy_account_details_factory(
    account_with_validate_deploy_class_hash: int,
    fee_contract: Contract,
) -> AccountToBeDeployedDetailsFactory:
    """
    Returns AccountToBeDeployedDetailsFactory.

    The Factory's get() method returns: address, key_pair, salt
    and class_hash of the account with validate deploy.
    Prefunds the address with enough tokens to allow for deployment.
    """
    return AccountToBeDeployedDetailsFactory(
        class_hash=account_with_validate_deploy_class_hash,
        fee_contract=fee_contract,
    )