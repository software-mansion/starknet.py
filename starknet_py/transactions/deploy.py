from typing import Union, List, Optional

from starkware.starknet.definitions.fields import ContractAddressSalt

from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.net.client_models import ContractClass
from starknet_py.net.models import Deploy


# pylint: disable=too-many-arguments
def make_deploy_tx(
    compilation_source: Optional[StarknetCompilationSource] = None,
    compiled_contract: Optional[Union[str, ContractClass]] = None,
    constructor_calldata: List[int] = None,
    salt: Optional[int] = None,
    version: int = 0,
    cairo_path: Optional[List[str]] = None,
) -> Deploy:
    if not constructor_calldata:
        constructor_calldata = []

    if isinstance(compiled_contract, str):
        compiled_contract = ContractClass.loads(compiled_contract)

    if not compiled_contract:
        compiled_contract = create_compiled_contract(
            compilation_source, compiled_contract, cairo_path
        )

    return Deploy(
        contract_address_salt=ContractAddressSalt.get_random_value()
        if salt is None
        else salt,
        contract_definition=compiled_contract,
        constructor_calldata=constructor_calldata,
        version=version,
    )
