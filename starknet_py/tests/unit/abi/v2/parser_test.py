import json
from typing import cast

import pytest

from starknet_py.abi.v2 import Abi, AbiParser
from starknet_py.cairo.data_types import UintType
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract


@pytest.mark.parametrize(
    "contract_name",
    [
        "AbiTypes",
        "Account",
        "ERC20",
        "Hello2",
        "HelloStarknet",
        "MinimalContract",
        "NewSyntaxTestContract",
        "TestContract",
        "TestEnum",
        "TestOption",
        "TokenBridge",
        "l1_l2",
    ],
)
def test_abi_parse(contract_name):
    abi = json.loads(
        load_contract(contract_name=contract_name, version=ContractVersion.V2)["sierra"]
    )["abi"]

    parser = AbiParser(abi)
    parsed_abi = parser.parse()

    assert isinstance(parsed_abi, Abi)


def test_bounded_int_parse_pre_2_8_0():
    abi_list = [
        {
            "type": "struct",
            "name": "core::circuit::u384",
            "members": [
                {
                    "name": "limb0",
                    "type": "core::internal::BoundedInt::<0, 79228162514264337593543950335>",
                },
                {
                    "name": "limb1",
                    "type": "core::internal::BoundedInt::<0, 79228162514264337593543950335>",
                },
                {
                    "name": "limb2",
                    "type": "core::internal::BoundedInt::<0, 79228162514264337593543950335>",
                },
                {
                    "name": "limb3",
                    "type": "core::internal::BoundedInt::<0, 79228162514264337593543950335>",
                },
            ],
        }
    ]

    parser = AbiParser(abi_list)
    parsed_abi = parser.parse()

    assert isinstance(parsed_abi, Abi)

    uint = cast(
        UintType, parsed_abi.defined_structures["core::circuit::u384"].types["limb0"]
    )
    assert uint.bits == 96


def test_bounded_int_parse_post_2_8_0():
    abi_list = [
        {
            "type": "struct",
            "name": "core::circuit::u384",
            "members": [
                {
                    "name": "limb0",
                    "type": "core::internal::bounded_int::BoundedInt::<0, 79228162514264337593543950335>",
                },
                {
                    "name": "limb1",
                    "type": "core::internal::bounded_int::BoundedInt::<0, 79228162514264337593543950335>",
                },
                {
                    "name": "limb2",
                    "type": "core::internal::bounded_int::BoundedInt::<0, 79228162514264337593543950335>",
                },
                {
                    "name": "limb3",
                    "type": "core::internal::bounded_int::BoundedInt::<0, 79228162514264337593543950335>",
                },
            ],
        }
    ]

    parser = AbiParser(abi_list)
    parsed_abi = parser.parse()

    assert isinstance(parsed_abi, Abi)

    uint = cast(
        UintType, parsed_abi.defined_structures["core::circuit::u384"].types["limb0"]
    )
    assert uint.bits == 96
