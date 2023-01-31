Serializers
===========

.. py:module:: starknet_py.serialization

Containers
----------
.. autoclass:: TupleDataclass
    :exclude-members: __init__, __new__
    :members: as_tuple, as_dict

Factory functions
-----------------

.. autofunction:: serializer_for_function
.. autofunction:: serializer_for_event
.. autofunction:: serializer_for_type

Specific serializers
--------------------

.. autoclass:: CairoDataSerializer
    :exclude-members: __init__, __new__
    :members: serialize, deserialize
.. autoclass:: PayloadSerializer
    :exclude-members: __init__, __new__
    :members: serialize, deserialize
.. autoclass:: FunctionSerializationAdapter
    :exclude-members: __init__, __new__
    :members: serialize, deserialize

Exceptions
----------

.. autoclass:: CairoSerializerException
    :exclude-members: __init__, __new__
.. autoclass:: InvalidTypeException
    :exclude-members: __init__, __new__
.. autoclass:: InvalidValueException
    :exclude-members: __init__, __new__

Deprecated old API
------------------

.. attention::
    ``data_transformer`` module has been deprecated. Use serialization module described above.

.. autoclass:: starknet_py.utils.data_transformer.data_transformer.CairoSerializer
    :members: