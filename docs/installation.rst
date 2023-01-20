Installation
============

To use StarkNet.py, ``ecdsa, fastecdsa, sympy`` dependencies are required. Depending on the operating system,
different installation steps must be performed.

Linux
-----

.. code-block:: bash

    sudo apt install -y libgmp3-dev
    pip install starknet-py

MacOS
-----

Instructions assume `Homebrew <https://brew.sh/>`_ being installed.

.. hint:: If you are experiencing issues installing StarkNet.py related to ``fastecdsa`` on recent versions of MacOS
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

This library is incompatible with Windows devices.
Use virtual machine with Linux, `Windows Subsystem for Linux 2 <https://learn.microsoft.com/en-us/windows/wsl/>`_ (WSL2) or other solution.
