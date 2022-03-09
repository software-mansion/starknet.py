from typing import List, NewType, Optional, Union

from starkware.starknet.services.api.contract_definition import ContractDefinition

from starknet_py.utils.compiler.starknet_compile import starknet_compile

CairoSourceCode = NewType("CairoSourceCode", str)
CairoFilename = NewType("CairoFilename", str)
StarknetCompilationSource = NewType(
    "CairoSource", Union[CairoSourceCode, List[CairoFilename]]
)


class Compiler:
    """
    Class for compiling Cairo contracts
    """

    def __init__(self):
        pass

    @staticmethod
    def create_contract_definition(
        compiled_contract: Optional[str] = None,
        contract_source: Optional[StarknetCompilationSource] = None,
        search_paths: Optional[List[str]] = None,
    ) -> ContractDefinition:
        """
        Creates ContractDefinition either from already compiled contract or contract source code

        :param compiled_contract: an already compiled contract
        :param contract_source: string containing source code or a list of source files paths
        :param search_paths: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
        :return a ContractDefinition
        """
        if not contract_source and not compiled_contract:
            raise ValueError(
                "One of compiled_contract or compilation_source is required."
            )

        if not compiled_contract:
            compiled_contract = Compiler.compile_contract(
                compilation_source=contract_source, search_paths=search_paths
            )

        return ContractDefinition.loads(compiled_contract)

    @staticmethod
    def compile_contract(
        compilation_source: StarknetCompilationSource,
        search_paths: Optional[List[str]] = None,
    ) -> str:
        """
        Compiles a contract and returns it as string

        :param compilation_source: string containing source code or a list of source files paths
        :param search_paths: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
        :return string of compiled contract
        """
        return starknet_compile(compilation_source, search_paths=search_paths)
