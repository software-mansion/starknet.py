import asyncio
import unittest
from random import randrange

from starknet_python_sdk.contract import Contract

abi = [
    {
        "inputs": [
            {
                "name": "key",
                "type": "felt"
            },
            {
                "name": "amount",
                "type": "felt"
            }
        ],
        "name": "increase_balance",
        "outputs": [],
        "type": "function"
    },
    {
        "inputs": [
            {
                "name": "key",
                "type": "felt"
            }
        ],
        "name": "get_balance",
        "outputs": [
            {
                "name": "res",
                "type": "felt"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

contract_hash = int("0x064bb3dc62fe6ce16f386305ce7e55fca81d9949c2f5b2efc9d25f35dec69b33", 16)


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()

    return wrapper

# TODO: Remove
class TestCase(unittest.TestCase):
    @async_test
    async def test_call(self):
        contract = Contract(contract_hash, abi)

        result = await contract.functions.get_balance.call(key=1234)

        self.assertListEqual(['0xb'], result)

    @async_test
    async def test_invoke(self):
        key = randrange(1, 1_000_000_000)
        contract = Contract(
            int("0x064bb3dc62fe6ce16f386305ce7e55fca81d9949c2f5b2efc9d25f35dec69b33", 16),
            abi
        )

        result = await contract.functions.increase_balance.invoke(key=key, amount=2137)
        await result.wait_for_acceptance()
        result = await contract.functions.get_balance.call(key=key)

        self.assertListEqual(['0x859'], result)
