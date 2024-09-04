import json

class ScarbOutputImporter:
    def __init__(self, sierra_path, casm_path, abi_path):
        # Initialize the class with paths to the sierra, casm, and abi files
        self.sierra_path = "test_data/test_sierra.sierra"
        self.casm_path = "test_data/test_sierra.casm"
        self.abi_path ="test_data/test_abi.json"
    
    def read_sierra(self):
        # Open and read the content of the sierra file
        with open(self.sierra_path, 'r') as file:
            return file.read()

    def read_casm(self):
        # Open and read the content of the casm file
        with open(self.casm_path, 'r') as file:
            return file.read()

    def read_abi(self):
        # Open and read the content of the abi file (assuming it's in JSON format)
        with open(self.abi_path, 'r') as file:
            return json.load(file)

    def calculate_compiled_contract_casm(self):
        # Read the content of sierra, casm, and abi
        sierra_content = self.read_sierra()
        casm_content = self.read_casm()
        abi_content = self.read_abi()
        
        # Example logic to calculate compiled_contract_casm
        # (You will need to implement the actual logic based on your needs)
        compiled_contract_casm = f"Compiled CASM from {sierra_content[:10]}... and {casm_content[:10]}... with ABI: {json.dumps(abi_content)[:10]}..."
        
        return compiled_contract_casm
