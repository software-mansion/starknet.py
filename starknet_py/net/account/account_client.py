from dataclasses import dataclass
from typing import Dict, Optional

from starkware.crypto.signature.signature import (
    private_to_stark_key,
    get_random_private_key,
)

from starkware.starknet.public.abi import get_selector_from_name


from starknet_py.net import Client
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.net.models import InvokeFunction, StarknetChainId, TransactionType
from starknet_py.net.networks import Network
from starknet_py.utils.sync import add_sync_methods
from starknet_py.utils.crypto.facade import message_signature, hash_message
from starknet_py.net.models.address import AddressRepresentation, parse_address


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
    Extends the functionality of :obj:`Client <starknet_py.net.Client>`, adding additional methods for creating the
    account contract
    """

    def __init__(
        self,
        address: AddressRepresentation,
        key_pair: KeyPair,
        net: Network,
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
        net: str,
        private_key: Optional[int] = None,
        chain: Optional[StarknetChainId] = None,
    ) -> "AccountClient":
        """
        Creates the account using
        `OpenZeppelin Account contract
        <https://github.com/OpenZeppelin/cairo-contracts/blob/main/contracts/Account.cairo>`_

        :param net: Target net's address or one of "mainnet", "testnet"
        :param chain: Chain used by the network. Required if you use a custom URL for ``net`` param
        :param private_key: Public Key used for the account
        :return: Instance of AccountClient which interacts with created account on given network
        """
        if not private_key:
            private_key = get_random_private_key()

        key_pair = KeyPair.from_private_key(private_key)

        client = Client(net=net, chain=chain)
        result = await client.deploy(
            constructor_calldata=[key_pair.public_key],
            compiled_contract=COMPILED_ACCOUNT_CONTRACT,
        )
        await client.wait_for_tx(
            tx_hash=result["transaction_hash"],
        )

        return AccountClient(
            net=net,
            chain=chain,
            address=result["address"],
            key_pair=key_pair,
        )
