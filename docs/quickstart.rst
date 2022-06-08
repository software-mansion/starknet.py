Quickstart
==========

Using Client
------------
:obj:`Client <starknet_py.net.Client>` is a facade for interacting with Starknet. It requires information about used network:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_client.py
    :language: python
    :lines: 8-29
    :dedent: 4

The default interface is asynchronous. Although it is the recommended way of using Starknet.py, you can also use a
synchronous version. It might be helpful to play with Starknet directly in python interpreter.

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_testnet_client.py
    :language: python
    :lines: 11-14
    :dedent: 4

You can see all Client's methods :obj:`here <starknet_py.net.Client>`.

Using AccountClient
-------------------

:obj:`AccountClient <starknet_py.net.account.account_client.AccountClient>` is an extension of a regular :obj:`Client <starknet_py.net.Client>`. It leverages `OpenZeppelin's Cairo contracts <https://github.com/OpenZeppelin/cairo-contracts>`_ to create an account contract which proxies (and signs) the calls to other contracts on Starknet.

Example usage:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_account_client.py
    :language: python
    :lines: 14-16,20-43
    :dedent: 4

Using Contract
--------------
:obj:`Contract <starknet_py.contract.Contract>` makes interacting with contracts deployed on Starknet much easier:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_using_contract.py
    :language: python
    :lines: 16-25,38-40,46-63
    :dedent: 4

Although asynchronous API is recommended, you can also use Contract's synchronous API:

.. literalinclude:: ../starknet_py/tests/e2e/docs/quickstart/test_synchronous_api.py
    :language: python
    :lines: 14-21,35-42
    :dedent: 4
