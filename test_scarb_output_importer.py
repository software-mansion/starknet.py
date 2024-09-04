import unittest
from scarb_output_importer import ScarbOutputImporter

class TestScarbOutputImporter(unittest.TestCase):

    def setUp(self):
        # Paths to your test files
        self.sierra_path = (r"test_data/test_sierra.sierra")
        self.casm_path = (r"test_data/test_casm.casm")
        self.abi_path = (r"test_data/test_abi.json")
        self.importer = ScarbOutputImporter(self.sierra_path, self.casm_path, self.abi_path)

    def test_read_sierra(self):
        result = self.importer.read_sierra()
        self.assertIsInstance(result, str)  # Check if result is a string
        self.assertTrue(len(result) > 0)    # Check if the string is not empty

    def test_read_casm(self):
        result = self.importer.read_casm()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_read_abi(self):
        result = self.importer.read_abi()
        self.assertIsInstance(result, dict)  # Assuming ABI is in JSON and should be a dictionary
        self.assertIn('some_key', result)    # Replace 'some_key' with an expected key in the ABI

    def test_calculate_compiled_contract_casm(self):
        result = self.importer.calculate_compiled_contract_casm()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()
