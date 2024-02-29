Development
===========

This page describes how to setup development environment. You don't need to follow the instructions if you just use starknet.py
as a package.


Development dependencies
------------------------
- `poetry <https://python-poetry.org/>`_ - dependency manager.
- `pyenv <https://github.com/pyenv/pyenv>`_ - recommended for installing and switching python versions locally.
- `cairo-lang <https://pypi.org/project/cairo-lang/>`_ - required to compile contracts  (`poe compile_contracts`)

Setup
-----

In order to run tests on devnet, you need to install `starknet-devnet-rs <https://github.com/0xSpaceShard/starknet-devnet-rs>`_.
The correct version of devnet to use corresponds to the Starknet and RPC specification that are currently supported by Starknet.py.
Information about the supported version for the latest release can be found in the :doc:`migration guide<migration_guide>`.

To avoid version discrepancies or other related issues, we recommend installing this dependency using the ``cargo install`` command, and specifying a certain commit along with the correct Starknet and RPC versions.

Below is the command you can use to do this, designed for compatibility with the current version of Starknet.py:

.. code-block:: bash

    cargo install \
    --locked \
    --git https://github.com/0xSpaceShard/starknet-devnet-rs.git \
    --rev 79a90fd

If you choose to install `starknet-devnet-rs <https://github.com/0xSpaceShard/starknet-devnet-rs>`_ using a different method, please make sure to add the executable ``starknet-devnet`` to your ``PATH`` environment variable.

In order to be able to run tests on testnet and integration networks (``starknet_py/tests/e2e/tests_on_networks/``), you must set some environmental variables:

    - ``GOERLI_INTEGRATION_RPC_URL``
    - ``GOERLI_TESTNET_RPC_URL``
    - ``SEPOLIA_INTEGRATION_RPC_URL``
    - ``SEPOLIA_TESTNET_RPC_URL``
    - ``GOERLI_INTEGRATION_ACCOUNT_PRIVATE_KEY``
    - ``GOERLI_INTEGRATION_ACCOUNT_ADDRESS``
    - ``GOERLI_TESTNET_ACCOUNT_PRIVATE_KEY``
    - ``GOERLI_TESTNET_ACCOUNT_ADDRESS``

The existing tests don't execute any invoke transactions on the Sepolia networks. If you plan to incorporate such tests, please also set the following environment variables:

    - ``SEPOLIA_INTEGRATION_ACCOUNT_PRIVATE_KEY``
    - ``SEPOLIA_INTEGRATION_ACCOUNT_ADDRESS``
    - ``SEPOLIA_TESTNET_ACCOUNT_PRIVATE_KEY``
    - ``SEPOLIA_TESTNET_ACCOUNT_ADDRESS``

The best way to set environment variables is to create ``test-variables.env`` file in ``starknet_py/tests/e2e/`` directory, so they can be loaded by the ``python-dotenv`` library.
You can find an example file ``test-variables.env.template`` in the same directory with the format of how it should look like.

.. code-block:: bash

    # Install dependencies
    poetry install

    # Compile contracts
    poe compile_contracts

    # Make sure everything was installed properly
    poe test


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
