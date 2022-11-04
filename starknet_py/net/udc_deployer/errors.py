class DeployerError(Exception):
    """
    Base class for all errors raised by Deployer
    """


class ContractDeployedEventNotFound(DeployerError):
    """
    ContractDeployed event was not found
    """

    def __init__(self, transaction_hash: str):
        super().__init__(
            f"ContractDeployed event was not found at the given transaction: {transaction_hash}"
            "Make sure that transaction_hash is the hash of UDC deploy transaction"
        )
