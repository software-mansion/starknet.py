from dataclasses import dataclass
from typing import Dict, Optional

from starkware.crypto.signature.signature import (
    private_to_stark_key,
    get_random_private_key,
)
from starkware.starknet.definitions.transaction_type import TransactionType
from starkware.starknet.public.abi import get_selector_from_name


from starknet.contract import Contract
from starknet.net import Client
from starknet.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet.utils.sync import add_sync_methods
from starknet.utils.crypto.facade import message_signature, hash_message
from starknet.utils.types import (
    AddressRepresentation,
    parse_address,
    InvokeFunction,
)


@dataclass
class KeyPair:
    private_key: int
    public_key: int

    @staticmethod
    def from_private_key(key: int) -> "KeyPair":
        return KeyPair(private_key=key, public_key=private_to_stark_key(key))


@add_sync_methods
class AccountClient(Client):
    """
    Extends the functionality of :obj:`Client <starknet.net.Client>`, adding additional methods for creating the
    account contract
    """

    def __init__(
        self,
        address: AddressRepresentation,
        key_pair: KeyPair,
        net: str,
        *args,
        **kwargs,
    ):
        super().__init__(net, *args, **kwargs)
        self.address = parse_address(address)
        self._key_pair = key_pair

    @property
    def private_key(self) -> int:
        return self._key_pair.private_key

    async def add_transaction(
        self,
        tx: InvokeFunction,
        token: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        :param tx: Transaction which invokes another contract through account proxy.
                   Signed transactions aren't supported at the moment
        :param token: Optional token for Starknet API access, appended in a query string
        :return: API response dictionary with `code`, `transaction_hash`
        """
        if tx.tx_type == TransactionType.DEPLOY:
            return await super().add_transaction(tx, token)

        if tx.signature:
            raise TypeError(
                "Adding signatures to a signer tx currently isn't supported"
            )

        result = await super().call_contract(
            InvokeFunction(
                contract_address=self.address,
                entry_point_selector=get_selector_from_name("get_nonce"),
                calldata=[],
                signature=[],
            )
        )
        nonce = result[0]

        msg_hash = hash_message(
            account=self.address,
            to_addr=tx.contract_address,
            selector=tx.entry_point_selector,
            calldata=tx.calldata,
            nonce=nonce,
        )
        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=msg_hash, priv_key=self.private_key)

        return await super().add_transaction(
            InvokeFunction(
                entry_point_selector=get_selector_from_name("execute"),
                calldata=[
                    tx.contract_address,
                    tx.entry_point_selector,
                    len(tx.calldata),
                    *tx.calldata,
                    nonce,
                ],
                contract_address=self.address,
                signature=[r, s],
            )
        )

    @staticmethod
    async def create_account(
        net: str, private_key: Optional[int] = None
    ) -> "AccountClient":
        """
        Creates the account using
        `OpenZeppelin Account contract
        <https://github.com/OpenZeppelin/cairo-contracts/blob/main/contracts/Account.cairo>`_

        :param net: Target net's address or one of "mainnet", "testnet"
        :param private_key: Public Key used for the account
        :return: Instance of AccountClient which interacts with created account on given network
        """
        if not private_key:
            private_key = get_random_private_key()

        key_pair = KeyPair.from_private_key(private_key)

        client = Client(net=net)
        account_contract = await Contract.deploy(
            client=client,
            constructor_args=[key_pair.public_key],
            compiled_contract=COMPILED_ACCOUNT_CONTRACT,
        )

        return AccountClient(
            net=net,
            address=account_contract.address,
            key_pair=key_pair,
        )
