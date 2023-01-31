Abi
===

Module containing representation of contract abi and parser for creating it from parsed json.

.. py:module:: starknet_py.abi

Parsing abi
-----------

.. autoclass:: AbiParser
    :members: parse

.. autoclass:: AbiParsingError
    :exclude-members: __init__, __new__

Model
-----------

.. autoclass:: Abi
    :exclude-members: __init__, __new__
    :members: defined_structures, functions, constructor, l1_handler, events

.. autoclass:: starknet_py.abi.Abi.Function

.. autoclass:: starknet_py.abi.Abi.Event
