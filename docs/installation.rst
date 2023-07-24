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

You might encounter problems related to ``libcrypto_c_exports``.

In such case make sure that you have `MinGW <https://www.mingw-w64.org/>`_ installed and up-to-date.

.. hint::
    An easy way to install MinGW is through `chocolatey <https://community.chocolatey.org/packages/mingw>`_.

    You also should have MinGW in your PATH environment variable (e.g. ``C:\ProgramData\chocolatey\lib\mingw\tools\install\mingw64\bin``).


If you encounter any further problems related to installation, you can create an `issue at our GitHub <https://github.com/software-mansion/starknet.py/issues/new?assignees=&labels=bug&projects=&template=bug_report.yaml&title=%5BBUG%5D+%3Ctitle%3E>`_
or ask for help in ``#🐍 | starknet-py`` channel on `Starknet Discord server <https://starknet.io/discord>`_.

2. Use virtual machine with Linux, `Windows Subsystem for Linux 2 <https://learn.microsoft.com/en-us/windows/wsl/>`_ (WSL2).
