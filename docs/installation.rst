Installation
============

To use StarkNet.py, ``ecdsa, fastecdsa, sympy`` dependencies are required. Depending on the operating system,
different install steps must be performed.

Linux
^^^^^

.. code-block:: console

    sudo apt install -y libgmp3-dev
    pip install starknet-py

MacOS with Intel processor
^^^^^^^^^^^^^^^^^^^^^^^^^^

Requires `Homebrew <https://brew.sh/>`_  installation.

.. code-block:: console

    brew install gmp
    pip install starknet-py

MacOS with Apple silicon
^^^^^^^^^^^^^^^^^^^^^^^^

Requires `Homebrew <https://brew.sh/>`_  installation.
First install gmp:

.. code-block:: console

    brew install gmp

Then install required dependencies and StarkNet.py itself:

.. code-block:: console

    CFLAGS=-I`brew --prefix gmp`/include LDFLAGS=-L`brew --prefix gmp`/lib pip install ecdsa fastecdsa sympy
    pip install starknet-py

Windows
^^^^^^^

This library is incompatible with Windows devices.
Use virtual machine with Linux, Windows Subsystem for Linux 2 (WSL2) or other solution.
