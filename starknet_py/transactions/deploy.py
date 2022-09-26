import warnings
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
    constructor_calldata: Optional[List[int]] = None,
    salt: Optional[int] = None,
    version: int = 0,
    cairo_path: Optional[List[str]] = None,
) -> Deploy:
    """
    Create deploy tx.
    Either `compilation_source` or `compiled_contract` is required.

    :param compilation_source: string containing source code or a list of source files paths
    :param compiled_contract: string containing compiled contract bytecode.
                              Useful for reading compiled contract from a file
    :param constructor_calldata: Calldata to be passed to contract constructor
    :param salt: Salt to be used when generating contract address
    :param version: PreparedFunctionCall version
    :param cairo_path: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
    :return: A "Deploy" transaction object

    .. deprecated:: 0.5.0
        Deploy transactions will not be supported in the future versions of StarkNet. Consider transitioning
        to Declare transactions and deploying through cairo syscall.
    """
    warnings.warn(
        "Deploy transactions will not be supported in the future versions of StarkNet. "
        "Consider transitioning to Declare transactions and deploying through cairo syscall.",
        category=DeprecationWarning,
    )

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
