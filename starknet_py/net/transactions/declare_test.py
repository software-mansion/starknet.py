from starknet_py.net.models.transaction import Declare
from starknet_py.net.transactions.declare import make_declare_tx


def test_make_declare_tx():
    declare = make_declare_tx(
        compilation_source="""
            %lang starknet
        
            @view
            func get_1() -> (res: felt) {
                return (1,);
            }
        """
    )
    assert isinstance(declare, Declare)
    assert [fn for fn in declare.contract_class.abi if fn["name"] == "get_1"]
