from starknet_py.hash.address import compute_address


def test_compute_address():
    assert (
        compute_address(
            class_hash=951442054899045155353616354734460058868858519055082696003992725251069061570,
            constructor_calldata=[21, 37],
            salt=1111,
        )
        == 1357105550695717639826158786311415599375114169232402161465584707209611368775
    )


def test_compute_address_with_deployer_address():
    assert (
        compute_address(
            class_hash=951442054899045155353616354734460058868858519055082696003992725251069061570,
            constructor_calldata=[21, 37],
            salt=1111,
            deployer_address=1234,
        )
        == 3179899882984850239687045389724311807765146621017486664543269641150383510696
    )
