import asyncio
import unittest

from .sync import add_sync_version


@add_sync_version
class Function:
    def __init__(self):
        self.name = "function X"

    async def call(self):
        await asyncio.sleep(0.1)
        return 1

    async def failure(self):
        raise Exception("Error")

    def get_name(self):
        return self.name


@add_sync_version
class Repository:
    def __init__(self):
        self.function = Function()

    async def get_function(self):
        await asyncio.sleep(0.1)
        return self.function


@add_sync_version
class Contract:
    def __init__(self, address):
        self.address = address

    @staticmethod
    async def get_repository():
        await asyncio.sleep(0.1)
        return Repository()

    @classmethod
    async def example_class_method(cls):
        await asyncio.sleep(0.1)
        return 2


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
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
        contract = Contract.sync("1")
        repository = contract.get_repository()
        function = repository.get_function()

        call_result = function.call()
        name = function.get_name()
        class_result = contract.example_class_method()

        self.assertEqual(call_result, 1)
        self.assertEqual(name, "function X")
        self.assertEqual(class_result, 2)
        with self.assertRaises(Exception):
            function.failure()
