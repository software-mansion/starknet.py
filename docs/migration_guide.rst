0.5.0 Migration guide
=====================

0.5.0 updates project to support cairo 0.10.0

New transaction version
=======================

Cairo 0.10.0 brings new version of the transaction.
The differences:

- ``contract_address`` field is now called ``account_contract_address``
- The field ``entry_point_selector`` is removed
- A nonce field is added

For now both (0 nad 1) transaction versions will be accepted but there will be a DeprecationWarning while using version 0.

AccountClient
=============

AccountClient's constructor has a new parameter now. ``supported_tx_version`` is used to differentiate between old and new accounts.
It is set to 0 as default so there is no need to set it while using old account.

.. note::

    In the future versions default value of ``supported_tx_version`` will be changed to 1. This will happen when the old account is deprecated.

