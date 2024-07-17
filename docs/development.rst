Development
===========

This page describes how to setup development environment. You don't need to follow the instructions if you just use starknet.py
as a package.


Development dependencies
------------------------
- `poetry <https://python-poetry.org/>`_ - dependency manager.
- `pyenv <https://github.com/pyenv/pyenv>`_ - recommended for installing and switching python versions locally.
- `cairo-lang <https://pypi.org/project/cairo-lang/>`_ - required to compile contracts  (`poe compile_contracts`)
- `asdf <https://asdf-vm.com/>`_ - required to install `scarb`, that is used for contracts compilation  (`poe compile_contracts`)

Setup
-----

Starknet devnet
^^^^^^^^^^^^^^^

To install `starknet-devnet-rs <https://github.com/0xSpaceShard/starknet-devnet-rs>`_ run the script ``./starknet_py/tests/install_devnet.sh``.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

In order to be able to run tests on testnet network (``starknet_py/tests/e2e/tests_on_networks/``), you must set some environmental variables:

    - ``SEPOLIA_RPC_URL``
    - ``SEPOLIA_ACCOUNT_PRIVATE_KEY``
    - ``SEPOLIA_ACCOUNT_ADDRESS``

The best way to set environment variables is to create ``test-variables.env`` file in ``starknet_py/tests/e2e/`` directory, so they can be loaded by the ``python-dotenv`` library.
You can find an example file ``test-variables.env.template`` in the same directory with the format of how it should look like.

Dependencies
^^^^^^^^^^^^

.. code-block:: bash

    poetry install

Contracts
^^^^^^^^^

.. code-block:: bash

    poe compile_contracts

Git hooks
---------
Run this snippet to enable lint checks and automatic formatting before commit/push.

.. code-block:: bash

    cp pre-push ./.git/hooks/
    cp pre-commit ./.git/hooks/
    chmod +x ./.git/hooks/pre-commit
    chmod +x ./.git/hooks/pre-push

Documentation
-------------
`Sphinx <https://www.sphinx-doc.org/en/master/>`_ is used for generating documentation.

.. code-block:: bash

    # Install additional dependencies for docs
    poetry install -E docs

    # Generate HTML documentation
    poe docs_create

    # Open generated HTML documentation
    poe docs_open

Tests
-----

.. code-block:: bash

    # Run whole suite
    poe test

    # Run only tests on networks
    poe test_ci_on_networks

    # Run unit tests and tests on devnet
    poe test_ci

    # Generate test report in terminal
    poe test_report

    # Generate HTML report and open it in the browser
    poe test_html

Code style guide
----------------

Rules to follow when writing a code:

1. Check the code with pylint

.. code-block:: bash

    poe lint

2. Format the code with black

.. code-block:: bash

    poe format

3. Run a typechecker (pyright)

.. code-block:: bash

    poe typecheck

4. Add constant values to the constants.py file.
5. Prefer keyword-only arguments where appropriate.
6. All public classes providing async api should be marked with the `@add_sync_methods` decorator.
7. Error messages should start with a capital letter.
8. Use `Argument x is...` instead of `X is...` when error message starts with argument (property) name.
9. All sentences (in docstrings/errors) should be ended with a period.
10. When adding a TODO comment, it must have a corresponding issue to it. The format for the comment is: ``# TODO (#issue no.): ...``.

Release checklist
-------------------

Perform these actions before releasing a new starknet.py version

1. Bump package version in ``pyproject.toml``
2. Re-lock using ``poetry lock --no-update``
3. Make a PR to development with name of format ``vMAJOR.MINOR.PATCHES-alpha`` and merge it making sure that the merge commit message is the same as PR name
4. Merge development into master without squashing

.. code-block:: bash

    git checkout master
    git merge development

5. Make a new release on GitHub
6. Run release action from ``master`` branch
