import warnings
from typing import Optional, List

from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
)

from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.net.client_models import Declare


def make_declare_tx(
    compilation_source: Optional[StarknetCompilationSource] = None,
    compiled_contract: Optional[str] = None,
    version: int = 0,
    cairo_path: Optional[List[str]] = None,
) -> Declare:
    """
    Create declaration tx.
    Either `compilation_source` or `compiled_contract` is required.

    :param compilation_source: string containing source code or a list of source files paths
    :param compiled_contract: string containing compiled contract bytecode.
                              Useful for reading compiled contract from a file
    :param version: PreparedFunctionCall version
    :param cairo_path: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
    :return: A "Declare" transaction object

    .. deprecated:: 0.5.0
        Unsigned declare transactions will not be supported in the future versions of StarkNet.
        Use :meth:`AccountClient.create_declare_transaction` instead.
    """
    warnings.warn(
        "Unsigned declare transactions will not be supported in the future versions of StarkNet. Please use "
        "AccountClient.sign_declare_transaction instead,",
        category=DeprecationWarning,
    )
    compiled_contract = create_compiled_contract(
        compilation_source, compiled_contract, cairo_path
    )
    return Declare(
        contract_class=compiled_contract,
        sender_address=DEFAULT_DECLARE_SENDER_ADDRESS,
        max_fee=0,
        signature=[],
        nonce=0,
        version=version,
    )
