Abi
===

Module containing representation of contract abi and parser for creating it from parsed json.

.. py:module:: starknet_py.abi.v2

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

.. autoclass:: starknet_py.abi.v2.Abi.Function
    :members:
    :undoc-members:
    :member-order: groupwise

.. autoclass:: starknet_py.abi.v2.Abi.Event
    :members:
    :undoc-members:
    :member-order: groupwise
