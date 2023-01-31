Data types
==========

Module containing representations of Cairo types. Mostly used to generate proper serializers.

.. py:module:: starknet_py.cairo.data_types

.. autoclass:: CairoType
    :exclude-members: __init__, __new__

.. autoclass:: FeltType
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
    :members: types
