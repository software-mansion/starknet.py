Installation
============

To install this package run

``pip install starknet.py``

or using Poetry:

``poetry add starknet.py``

.. _Crypto-cpp installation:

Using with `starkware-libs/crypto-cpp`
--------------------------------------

By default, ``crypto-cpp`` is used and so it must be configured properly:

1. Compile it from sources (https://github.com/starkware-libs/crypto-cpp)
2. Copy ``libcrypto_c_exports.dylib`` from ``crypto-cpp/src/starkware/crypto/ffi/libcrypto_c_exports.dylib`` to ``starknet_py/utils/crypto``

To use python implementation instead, ``DISABLE_CRYPTO_C_EXTENSION`` environment variable can be set to ``false``

.. code-block:: sh

    export DISABLE_CRYPTO_C_EXTENSION="false"
