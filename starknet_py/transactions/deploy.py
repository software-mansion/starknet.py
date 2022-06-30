from typing import Union, List, Optional

from starkware.starknet.definitions.fields import ContractAddressSalt

from starknet_py.net.client_models import ContractClass
from starknet_py.net.models import Deploy


def make_deploy_tx(
        compiled_contract: Union[ContractClass, str],
        constructor_calldata: List[int],
        salt: Optional[int] = None,
        version: int = 0,
) -> Deploy:
    if isinstance(compiled_contract, str):
        compiled_contract = ContractClass.loads(compiled_contract)

    return Deploy(
        contract_address_salt=ContractAddressSalt.get_random_value()
        if salt is None
        else salt,
        contract_definition=compiled_contract,
        constructor_calldata=constructor_calldata,
        version=version,
    )
