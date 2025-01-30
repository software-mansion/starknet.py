Data types
==========

Module containing representations of Cairo types. Mostly used to generate proper serializers.

.. py:module:: starknet_py.cairo.data_types

.. autoclass:: CairoType
    :exclude-members: __init__, __new__

.. autoclass:: FeltType
    :exclude-members: __init__, __new__

.. autoclass:: BoolType
    :exclude-members: __init__, __new__

.. autoclass:: TupleType
    :exclude-members: __init__, __new__
    :members: types

.. autoclass:: NamedTupleType
    :exclude-members: __init__, __new__
    :members: types

.. autoclass:: ArrayType
    :exclude-members: __init__, __new__
    :members: inner_type

.. autoclass:: StructType
    :exclude-members: __init__, __new__
    :members: name, types

.. autoclass:: EnumType
    :exclude-members: __init__, __new__
    :members: name, variants

.. autoclass:: OptionType
    :exclude-members: __init__, __new__
    :members: type

.. autoclass:: UintType
    :exclude-members: __init__, __new__
    :members: bits

.. autoclass:: UnitType
    :exclude-members: __init__, __new__

.. autoclass:: EventType
    :exclude-members: __init__, __new__
    :members: name, types, keys

.. autoclass:: NonZeroType
    :exclude-members: __init__, __new__
    :members: type