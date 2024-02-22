Abi
===

Module containing representation of contract abi and parser for creating it from parsed json.

.. py:module:: starknet_py.v0.abi

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

.. autoclass:: starknet_py.abi.v0.model.Function
    :members:
    :undoc-members:
    :member-order: groupwise

.. autoclass:: starknet_py.abi.v0.model.Event
    :members:
    :undoc-members:
    :member-order: groupwise
