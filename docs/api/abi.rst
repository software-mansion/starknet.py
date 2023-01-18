Abi
===

Module containing representation of contract abi and parser for creating it from parsed json.

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

.. autoclass:: Abi.Function

.. autoclass:: Abi.Event