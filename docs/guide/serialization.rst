Serialization
=============

Data serialization
-------------------

Starknet.py **serializes** python values to Cairo values and **deserializes** Cairo values to python values.

.. attention::
    Serializing short strings to felts has been deprecated. Please use `starknet_py.cairo.felt.encode_shortstring` to
    create numeric value from string _before_ passing value to serializer.

.. list-table:: Serialization from python to Cairo
   :widths: 25 25 25 25
   :header-rows: 1

   * - Expected Cairo type
     - Accepted python types
     - Example python values
     - Comment
   * - felt
     - int
     - ``0``, ``1``, ``1213124124``
     - Provided int must be in range [0;P) - P being the Prime used in cairo-vm.
   * - tuple
     - any iterable of matching size
     - ``(1, 2, (9, 8))``, ``[1, 2, (9, 8)]``, ``(v for v in [1, 2, (9, 8)])``
     - Can nest other types apart from pointers
   * - named tuple
     - dict or NamedTuple or :obj:`TupleDataclass <starknet_py.serialization.TupleDataclass>`
     - ``{"a": 1, "b": 2, "c" : (3, 4)}``, ``NamedTuple("name", [("a", int), ("b", int), ("c", tuple)])(1, 2, (3, 4))``
     -
   * - struct
     - dict with keys matching struct
     - ``{"key_1": 2, "key_2": (1, 2, 3), "key_3": {"other_struct_key": 13}}``
     - Can nest other types apart from pointers
   * - pointer/array (adds ``parameter_len`` parameter to abi)
     - any iterable
     - ``[1, 2, 3]``, ``[]``, ``({"low": 1, "high": 1}, {"low": 2, "high": 2})``
     - ``parameter_len`` is filled automatically from value
   * - uint256
     - int or dict with ``"low"`` and ``"high"`` keys and ints as values
     - ``0``, ``340282366920938463463374607431768211583``, ``{"low": 12, "high": 13}``
     -



.. list-table:: Deserialization from Cairo to python values
   :widths: 25 25
   :header-rows: 1

   * - Cairo type
     - Python type
   * - felt
     - int
   * - tuple
     - tuple
   * - named tuple
     - :obj:`TupleDataclass <starknet_py.serialization.TupleDataclass>`
   * - struct
     - dict with keys matching struct
   * - pointer/array
     - list
   * - unt256
     - int

Working with shortstrings
-------------------------

To make working with short strings easier we provide some utility functions to translate between them and felt values.
You can read more about how cairo treats shortstrings in
`the documentation <https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals>`_.

Conversion functions and references:

- :obj:`encode_shortstring <starknet_py.cairo.felt.encode_shortstring>`
- :obj:`decode_shortstring <starknet_py.cairo.felt.decode_shortstring>`

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_serializing.py
    :language: python
    :dedent: 4
    :start-after: docs-shortstring: start
    :end-before: docs-shortstring: end

Creating serializers from abi
-----------------------------
For most use cases using high level :obj:`Contract <starknet_py.contract.Contract>` is enough - it handles serialization
and deserialization for you. If you need more flexibility you can use lower level serialization API, see :ref:`Serializers`
for more details.

:obj:`AbiParser <starknet_py.net.models.abi.parser.AbiParser>` transforms ABI into
:obj:`Abi dataclass <starknet_py.net.models.abi.model.Abi>` that can be used for creating serializers. This way you can
easily deserialize events or serialize function's inputs.

Serializing function inputs and outputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_serializing.py
    :language: python
    :dedent: 4
    :start-after: docs-serializer: start
    :end-before: docs-serializer: end

Serializing events
^^^^^^^^^^^^^^^^^^

Events emitted by contracts can also be serialized, having provided the correct ABI

.. codesnippet:: ../../starknet_py/tests/e2e/docs/guide/test_serializing.py
    :language: python
    :dedent: 4
    :start-after: docs-event: start
    :end-before: docs-event: end
