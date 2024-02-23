Abi
===

Module containing representation of contract abi and parser for creating it from parsed json.

.. py:module:: starknet_py.abi.v2

Parsing abi v2
--------------

.. autoclass:: AbiParser
    :members: parse

.. autoclass:: AbiParsingError
    :exclude-members: __init__, __new__

Model v2
--------

.. autoclass:: Abi
    :exclude-members: __init__, __new__
    :members: defined_structures, functions, constructor, l1_handler, events, defined_enums, interfaces, implementations

.. autoclass:: starknet_py.abi.v2.Abi.Function
    :members:
    :undoc-members:
    :member-order: groupwise

.. autoclass:: starknet_py.abi.v2.Abi.Event
    :members:
    :undoc-members:
    :member-order: groupwise

.. py:module:: starknet_py.abi.v1

Parsing abi v1
--------------

.. autoclass:: AbiParser
    :members: parse

.. autoclass:: AbiParsingError
    :exclude-members: __init__, __new__

Model v1
--------

.. autoclass:: Abi
    :exclude-members: __init__, __new__
    :members: defined_structures, functions, events, defined_enums

.. autoclass:: starknet_py.abi.v1.Abi.Function
    :members:
    :undoc-members:
    :member-order: groupwise

.. autoclass:: starknet_py.abi.v1.Abi.Event
    :members:
    :undoc-members:
    :member-order: groupwise

.. py:module:: starknet_py.abi.v0

Parsing abi v0
--------------

.. autoclass:: AbiParser
    :members: parse

.. autoclass:: AbiParsingError
    :exclude-members: __init__, __new__

Model v0
--------

.. autoclass:: Abi
    :exclude-members: __init__, __new__
    :members: defined_structures, functions, constructor, l1_handler, events

.. autoclass:: starknet_py.abi.v0.Abi.Function
    :members:
    :undoc-members:
    :member-order: groupwise

.. autoclass:: starknet_py.abi.v0.Abi.Event
    :members:
    :undoc-members:
    :member-order: groupwise
