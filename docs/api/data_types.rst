Data types
==========

Module containing representations of Cairo types. Mostly used to generate proper serializers.

.. autoclass:: starknet_py.cairo.data_types.CairoType
    :exclude-members: __init__, __new__

.. autoclass:: starknet_py.cairo.data_types.FeltType
    :exclude-members: __init__, __new__

.. autoclass:: starknet_py.cairo.data_types.TupleType
    :exclude-members: __init__, __new__
    :members: types

.. autoclass:: starknet_py.cairo.data_types.NamedTupleType
    :exclude-members: __init__, __new__
    :members: types

.. autoclass:: starknet_py.cairo.data_types.ArrayType
    :exclude-members: __init__, __new__
    :members: inner_type

.. autoclass:: starknet_py.cairo.data_types.StructType
    :exclude-members: __init__, __new__
    :members: types
