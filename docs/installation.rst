Installation
============

To install this package run

``pip install starknet.py``

or using Poetry:

``poetry add starknet.py``

.. _Crypto-cpp installation:

Using with `starkware-libs/crypto-cpp`
--------------------------------------

To use the CPP library:

1. Compile it from sources (https://github.com/starkware-libs/crypto-cpp)
2. Provide the path to the library in ``CRYPTO_C_EXPORTS_PATH`` environment variable