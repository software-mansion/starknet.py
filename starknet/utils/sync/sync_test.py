import asyncio
import unittest

from starknet.utils.sync import add_sync_methods


@add_sync_methods
class Function:
    def __init__(self):
        self.name = "function X"

    @staticmethod
    async def call():
        await asyncio.sleep(0.1)
        return 1

    @staticmethod
    async def failure():
        raise Exception("Error")

    def get_name(self):
        return self.name


@add_sync_methods
class Repository:
    def __init__(self):
        self.function = Function()

    async def get_function(self):
        await asyncio.sleep(0.1)
        return self.function


# pylint: disable=no-member
@add_sync_methods
class Contract:
    def __init__(self, address):
        self.address = address

    @staticmethod
    async def get_repository():
        await asyncio.sleep(0.1)
        return Repository()

    @staticmethod
    async def example_class_method():
        await asyncio.sleep(0.1)
        return 2


def async_test(func):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(func)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


class TestAddSyncVersion(unittest.TestCase):
    @async_test
    async def test_asynchronous_versions(self):
        contract = Contract("1")
        repository = await contract.get_repository()
        function = await repository.get_function()

        call_result = await function.call()
        name = function.get_name()
        class_result = await contract.example_class_method()

        self.assertEqual(call_result, 1)
        self.assertEqual(name, "function X")
        self.assertEqual(class_result, 2)
        with self.assertRaises(Exception):
            await function.failure()

    def test_sync_versions(self):
        contract = Contract("1")
        repository = contract.get_repository_sync()
        function = repository.get_function_sync()

        call_result = function.call_sync()
        name = function.get_name()
        class_result = contract.example_class_method_sync()

        self.assertEqual(call_result, 1)
        self.assertEqual(name, "function X")
        self.assertEqual(class_result, 2)
        with self.assertRaises(Exception):
            function.failure_sync()
