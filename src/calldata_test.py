import unittest

from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from src.calldata import CalldataTransformer


class TestCase(unittest.TestCase):
    def transformer_for_function(self, inputs, structs=None):
        structs = structs or []
        fun_abi = {
            "inputs": inputs,
            "name": "test_fun",
            "outputs": [{"name": "value", "type": "felt"}],
            "stateMutability": "view",
            "type": "function",
        }
        full_abi = [fun_abi, *structs]
        return CalldataTransformer(
            abi=fun_abi, identifier_manager=identifier_manager_from_abi(full_abi)
        )

    def test_array(self):
        transformer = self.transformer_for_function(
            [{"name": "array_len", "type": "felt"}, {"name": "array", "type": "felt*"}]
        )

        result = transformer([1, 2, 3])

        self.assertListEqual(result, [3, 1, 2, 3])

    def test_empty_array(self):
        transformer = self.transformer_for_function(
            [{"name": "array_len", "type": "felt"}, {"name": "array", "type": "felt*"}]
        )

        result = transformer([])

        self.assertListEqual(result, [0])

    def test_felt(self):
        transformer = self.transformer_for_function([{"name": "value", "type": "felt"}])

        result = transformer(1234)

        self.assertListEqual(result, [1234])

    def test_struct(self):
        transformer = self.transformer_for_function(
            [{"name": "value", "type": "SimpleStruct"}],
            [
                {
                    "members": [
                        {"name": "first", "offset": 0, "type": "felt"},
                        {"name": "second", "offset": 1, "type": "(felt, felt, felt)"},
                    ],
                    "name": "SimpleStruct",
                    "size": 4,
                    "type": "struct",
                }
            ],
        )

        result = transformer({"first": 1, "second": (2, 3, 4)})

        self.assertListEqual(result, [1, 2, 3, 4])

    def test_nested_struct(self):
        transformer = self.transformer_for_function(
            [{"name": "value", "type": "StructWithStruct"}],
            [
                {
                    "members": [
                        {"name": "first", "offset": 0, "type": "NestedStruct"},
                        {"name": "second", "offset": 1, "type": "(felt, felt, felt)"},
                        {"name": "third", "offset": 2, "type": "DeeplyNestedStruct"},
                    ],
                    "name": "StructWithStruct",
                    "size": 4,
                    "type": "struct",
                },
                {
                    "members": [
                        {
                            "name": "deeply_nested",
                            "offset": 0,
                            "type": "DeeplyNestedStruct",
                        },
                    ],
                    "name": "NestedStruct",
                    "size": 1,
                    "type": "struct",
                },
                {
                    "members": [
                        {"name": "nested", "offset": 0, "type": "felt"},
                    ],
                    "name": "DeeplyNestedStruct",
                    "size": 1,
                    "type": "struct",
                },
            ],
        )

        result = transformer(
            {
                "first": {"deeply_nested": {"nested": 1}},
                "second": (2, 3, 4),
                "third": {"nested": 5},
            }
        )

        self.assertListEqual(result, [1, 2, 3, 4, 5])

    def test_multiple_values(self):
        transformer = self.transformer_for_function(
            [
                {"name": "first", "type": "felt"},
                {"name": "second_len", "type": "felt"},
                {"name": "second", "type": "felt*"},
                {"name": "third", "type": "(felt, felt)"},
            ],
        )

        result = transformer(1, second=[2, 3, 4, 5], third=(6, 7))

        self.assertListEqual(result, [1, 4, 2, 3, 4, 5, 6, 7])
