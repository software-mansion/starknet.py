Installation
============

To use StarkNet.py, ``ecdsa, fastecdsa, sympy`` dependencies are required. Depending on the operating system,
different installation steps must be performed.

Linux
-----

.. code-block:: console

    sudo apt install -y libgmp3-dev
    pip install starknet-py

MacOS
-----

Instructions assume `Homebrew <https://brew.sh/>`_ being installed.

Intel processor
^^^^^^^^^^^^^^^

.. code-block:: console

    brew install gmp
    pip install starknet-py

Apple silicon
^^^^^^^^^^^^^

.. code-block:: console

    brew install gmp
    CFLAGS=-I`brew --prefix gmp`/include LDFLAGS=-L`brew --prefix gmp`/lib pip install starknet-py

Windows
-------

This library is incompatible with Windows devices.
Use virtual machine with Linux, `Windows Subsystem for Linux 2 <https://learn.microsoft.com/en-us/windows/wsl/>`_ (WSL2) or other solution.
