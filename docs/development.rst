Development
===========

This page describes how to setup development environment. You don't need to follow the instructions if you just use starknet.py
as a package.


Development dependencies
------------------------
- `poetry <https://python-poetry.org/>`_ - dependency manager.
- `pyenv <https://github.com/pyenv/pyenv>`_ - recommended for installing and switching python versions locally.

Make sure running ``poetry run python --version`` returns ``Python 3.8.x``.

Setup
-----

.. code-block:: bash

    # Install dependencies
    poetry install

    # Compile contracts
    poe compile_contracts

    # Make sure everything was installed properly
    poe test

Crypto-cpp
----------
By default, the library uses `crypto_cpp_py <https://github.com/software-mansion-labs/crypto-cpp-py/>`_. To use python implementation instead, ``DISABLE_CRYPTO_C_EXTENSION`` environment variable can be set to ``false``

.. code-block:: sh

    export DISABLE_CRYPTO_C_EXTENSION="false"

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

    # Generate test report in terminal
    poe test_report

    # Generate HTML report and open it in the browser
    poe test_html

    # Run only unit tests
    poe test_unit

    # Run only e2e tests
    poe test_e2e

Running e2e tests in PyCharm
----------------------------
1. Run ``starkware-devnet`` script before running e2e tests in PyCharm.
2. Use ``E2E tests`` configuration to run or debug.

⚠️ **Warning**: Make sure to fill your interpreter in the configuration, to match your project's poetry venv.

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

Release checklist
-------------------

Perform these actions before releasing a new StarkNet.py version

1. Bump package version in ``pyproject.toml``
2. Re-lock using ``poetry lock --no-update``
3. Make a PR to development with name of format ``vMINOR.MAJOR.PATCHES-alpha`` and merge it making sure that the merge commit message is the same as PR name
4. Merge development into master without squashing

.. code-block:: bash

    git checkout master
    git merge development

5. Make a new release on GitHub
6. Run release action from ``master`` branch
