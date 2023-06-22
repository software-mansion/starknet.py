Installation
============

To use starknet.py, ``ecdsa, fastecdsa, sympy`` dependencies are required. Depending on the operating system,
different installation steps must be performed.

Linux
-----

.. code-block:: bash

    sudo apt install -y libgmp3-dev
    pip install starknet-py

MacOS
-----

Instructions assume `Homebrew <https://brew.sh/>`_ being installed.

.. hint:: If you are experiencing issues installing starknet.py related to ``fastecdsa`` on recent versions of MacOS
    consider installing ``cmake`` with version ``>=3.22.4``.

    .. code-block:: bash

        brew install cmake

    It is required to build `crypto-cpp-py <https://github.com/software-mansion-labs/crypto-cpp-py>`_
    dependency in case it hasn't been updated to support newest MacOS versions.

Intel processor
^^^^^^^^^^^^^^^

.. code-block:: bash

    brew install gmp
    pip install starknet-py

Apple silicon
^^^^^^^^^^^^^

.. code-block:: bash

    brew install gmp
    CFLAGS=-I`brew --prefix gmp`/include LDFLAGS=-L`brew --prefix gmp`/lib pip install starknet-py

Windows
-------

You can install starknet.py on Windows in two ways:

1. Install it just like you would on Linux.

You might encounter problems related to missing files in path (particularly when loading `libcrypto_c_exports`). Possible solutions are to:

    - install MinGW,
    - manually add required files (probably ``libgcc_s_seh-1.dll``, ``libstdc++-6.dll`` and ``libwinpthread-1.dll``) to your PATH.

If you encounter any other problems related to installation, you can ask for help in starknet-py channel on Starknet Discord server.

2. Use virtual machine with Linux, `Windows Subsystem for Linux 2 <https://learn.microsoft.com/en-us/windows/wsl/>`_ (WSL2) or other solution.
