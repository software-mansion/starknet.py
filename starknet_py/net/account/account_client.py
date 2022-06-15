from typing import Dict, Optional, List
from dataclasses import replace

from starkware.crypto.signature.signature import get_random_private_key
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.utils.data_transformer.data_transformer import DataTransformer
from starknet_py.net.client import Client
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.net.models import (
    InvokeFunction,
    StarknetChainId,
    TransactionType,
    Transaction,
)
from starknet_py.net.networks import Network, MAINNET, TESTNET
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner, KeyPair
from starknet_py.net.signer import BaseSigner
from starknet_py.utils.sync import add_sync_methods
from starknet_py.net.models.address import AddressRepresentation, parse_address


@add_sync_methods
class AccountClient(Client):
    """
    Extends the functionality of :obj:`Client <starknet_py.net.Client>`, adding additional methods for creating the
    account contract
    """

    def __init__(
        self,
        address: AddressRepresentation,
        net: Network,
        *args,
        signer: Optional[BaseSigner] = None,
        key_pair: Optional[KeyPair] = None,
        **kwargs,
    ):
        if signer is None and key_pair is None:
            raise ValueError(
                "Either a signer or a key_pair must be provied in AccountClient constructor"
            )
        super().__init__(net, *args, **kwargs)
        self.net = net
        self.address = parse_address(address)
        self.signer = signer or StarkCurveSigner(
            account_address=self.address, key_pair=key_pair, chain_id=self.chain
        )

    async def _get_nonce(self) -> int:
        [nonce] = await super().call_contract(
            InvokeFunction(
                contract_address=self.address,
                entry_point_selector=get_selector_from_name("get_nonce"),
                calldata=[],
                signature=[],
                max_fee=0,
                version=0,
            )
        )
        return nonce

    def _get_default_token_address(self) -> str:
        if self.net not in [TESTNET, MAINNET]:
            raise ValueError(
                "Token_address must be specified when using a custom net address"
            )

        return FEE_CONTRACT_ADDRESS

    async def get_balance(
        self, token_address: Optional[AddressRepresentation] = None
    ) -> int:
        """
        Checks account's balance of specified token.

        :param token_address: Address of the ERC20 contract.
                              If not specified it will be payment token (wrapped ETH) address.
        :return: Token balance
        """

        token_address = token_address or self._get_default_token_address()

        low, high = await super().call_contract(
            InvokeFunction(
                contract_address=parse_address(token_address),
                entry_point_selector=get_selector_from_name("balanceOf"),
                calldata=[self.address],
                signature=[],
                max_fee=0,
                version=0,
            )
        )

        return (high << 128) + low

    async def _prepare_execute_transaction(self, tx: InvokeFunction) -> Transaction:
        nonce = await self._get_nonce()

        calldata_py = [
            [
                {
                    "to": tx.contract_address,
                    "selector": tx.entry_point_selector,
                    "data_offset": 0,
                    "data_len": len(tx.calldata),
                }
            ],
            tx.calldata,
            nonce,
        ]

        code = await self.get_code(contract_address=parse_address(self.address))
        abi = code["abi"]
        identifier_manager = identifier_manager_from_abi(abi)
        [execute_abi] = [a for a in abi if a["name"] == "__execute__"]

        payload_transformer = DataTransformer(
            abi=execute_abi, identifier_manager=identifier_manager
        )

        wrapped_calldata, _ = payload_transformer.from_python(*calldata_py)

        return InvokeFunction(
            entry_point_selector=get_selector_from_name("__execute__"),
            calldata=wrapped_calldata,
            contract_address=self.address,
            signature=[],
            max_fee=tx.max_fee,
            version=tx.version,
        )

    async def _sign_transaction(self, tx: InvokeFunction):
        execute_tx = await self._prepare_execute_transaction(tx)
        signature = self.signer.sign_transaction(execute_tx)
        execute_tx = add_signature_to_transaction(execute_tx, signature)
        return execute_tx

    async def add_transaction(
        self,
        tx: InvokeFunction,
        token: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        :param tx: Transaction which invokes another contract through account proxy.
                   Signed transactions aren't supported at the moment
        :param token: Optional token for Starknet API access, appended in a query string
        :return: API response dictionary with `code`, `transaction_hash`
        """
        if tx.tx_type in (TransactionType.DECLARE, TransactionType.DEPLOY):
            return await super().add_transaction(tx, token)

        if tx.signature:
            raise TypeError(
                "Adding signatures to a signer tx currently isn't supported"
            )

        return await super().add_transaction(await self._sign_transaction(tx))

    async def estimate_fee(
        self,
        tx: InvokeFunction,
    ) -> int:
        """
        :param tx: Transaction which fee we want to calculate
        :return: Estimated fee
        """
        return await super().estimate_fee(await self._sign_transaction(tx))

    @staticmethod
    async def create_account(
        net: str,
        private_key: Optional[int] = None,
        signer: Optional[BaseSigner] = None,
        chain: Optional[StarknetChainId] = None,
    ) -> "AccountClient":
        """
        Creates the account using
        `OpenZeppelin Account contract
        <https://github.com/starkware-libs/cairo-lang/blob/4e233516f52477ad158bc81a86ec2760471c1b65/src/starkware/starknet/third_party/open_zeppelin/Account.cairo>`_

        :param net: Target net's address or one of "mainnet", "testnet"
        :param chain: Chain used by the network. Required if you use a custom URL for ``net`` param
        :param private_key: Private Key used for the account
        :param signer: Signer used to create account and sign transaction
        :return: Instance of AccountClient which interacts with created account on given network
        """
        if signer is None:
            private_key = private_key or get_random_private_key()

            key_pair = KeyPair.from_private_key(private_key)
            address = await deploy_account_contract(
                key_pair.public_key, net=net, chain=chain
            )
            signer = StarkCurveSigner(
                account_address=address, key_pair=key_pair, chain_id=chain
            )
        else:
            address = await deploy_account_contract(
                signer.public_key, net=net, chain=chain
            )

        return AccountClient(
            net=net,
            chain=chain,
            address=address,
            signer=signer,
        )


async def deploy_account_contract(
    public_key: int, net: str, chain: Optional[StarknetChainId] = None
) -> AddressRepresentation:
    client = Client(net=net, chain=chain)
    result = await client.deploy(
        constructor_calldata=[public_key],
        compiled_contract=COMPILED_ACCOUNT_CONTRACT,
    )
    await client.wait_for_tx(
        tx_hash=result["transaction_hash"],
    )
    return result["address"]


def add_signature_to_transaction(
    tx: InvokeFunction, signature: List[int]
) -> InvokeFunction:
    return replace(tx, signature=signature)
