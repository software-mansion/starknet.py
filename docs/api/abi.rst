Abi
===

Module containing representation of contract abi and parser for creating it from parsed json.


Parsing abi
-----------

.. autoclass:: starknet_py.abi.v2.parser.AbiParser
    :members: parse

.. autoclass:: starknet_py.abi.v2.parser.AbiParsingError
    :exclude-members: __init__, __new__

Model
-----------

.. autoclass:: starknet_py.abi.v2.model.Abi
    :exclude-members: __init__, __new__
    :members: defined_structures, functions, constructor, l1_handler, events

.. autoclass:: starknet_py.abi.v2.model.Abi.Function
    :members:
    :undoc-members:
    :member-order: groupwise

.. autoclass:: starknet_py.abi.v2.model.Abi.Event
    :members:
    :undoc-members:
    :member-order: groupwise
