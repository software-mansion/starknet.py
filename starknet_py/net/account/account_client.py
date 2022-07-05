from typing import Optional, List, Union
from dataclasses import replace

from starkware.crypto.signature.signature import get_random_private_key
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    CastableToHash,
)

from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    SentTransaction,
    Hash,
    DeclaredContract,
    Tag,
    TransactionReceipt,
    BlockStateUpdate,
    StarknetBlock,
    StarknetTransaction,
    Declare,
    Deploy,
)
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.net.models import (
    InvokeFunction,
    StarknetChainId,
    Transaction,
    BlockIdentifier,
    chain_from_network,
)
from starknet_py.net.networks import Network, MAINNET, TESTNET
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner, KeyPair
from starknet_py.net.signer import BaseSigner
from starknet_py.transactions.deploy import make_deploy_tx
from starknet_py.utils.data_transformer.execute_transformer import execute_transformer
from starknet_py.utils.sync import add_sync_methods
from starknet_py.net.models.address import AddressRepresentation, parse_address


@add_sync_methods
class AccountClient(Client):
    """
    Extends the functionality of :obj:`Client <starknet_py.net.client.Client>`,
    adding additional methods for creating the account contract.
    """

    def __init__(
        self,
        address: AddressRepresentation,
        client: Client,
        signer: Optional[BaseSigner] = None,
        key_pair: Optional[KeyPair] = None,
    ):
        # pylint: disable=too-many-arguments
        if signer is None and key_pair is None:
            raise ValueError(
                "Either a signer or a key_pair must be provied in AccountClient constructor"
            )

        chain = chain_from_network(net=client.net, chain=client.chain)

        if chain is None and client is None:
            raise ValueError("One of chain or client must be provided")
        self._net = client.net
        self.address = parse_address(address)
        self.client = client
        self.signer = signer or StarkCurveSigner(
            account_address=self.address, key_pair=key_pair, chain_id=self.client.chain
        )

    @property
    def chain(self) -> StarknetChainId:
        return self.client.chain

    @property
    def net(self) -> Network:
        return self._net

    async def get_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> StarknetBlock:
        return await self.client.get_block(
            block_hash=block_hash, block_number=block_number
        )

    async def get_state_update(self, block_hash: Union[Hash, Tag]) -> BlockStateUpdate:
        return await self.client.get_state_update(block_hash=block_hash)

    async def get_storage_at(
        self, contract_address: Hash, key: int, block_hash: Union[Hash, Tag]
    ) -> int:
        return await self.client.get_storage_at(
            contract_address=contract_address, key=key, block_hash=block_hash
        )

    async def get_transaction(self, tx_hash: Hash) -> Transaction:
        return self.client.get_transaction(tx_hash=tx_hash)

    async def get_transaction_receipt(self, tx_hash: Hash) -> TransactionReceipt:
        return await self.client.get_transaction_receipt(tx_hash=tx_hash)

    async def call_contract(
        self, invoke_tx: InvokeFunction, block_hash: Union[Hash, Tag] = None
    ) -> List[int]:
        return await self.client.call_contract(invoke_tx=invoke_tx)

    async def get_class_hash_at(self, contract_address: Hash) -> int:
        return await self.client.get_class_hash_at(contract_address=contract_address)

    async def get_class_by_hash(self, class_hash: Hash) -> DeclaredContract:
        return await self.client.get_class_by_hash(class_hash=class_hash)

    async def _get_nonce(self) -> int:
        [nonce] = await self.call_contract(
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

        low, high = await self.call_contract(
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

        wrapped_calldata, _ = execute_transformer.from_python(*calldata_py)

        return InvokeFunction(
            entry_point_selector=get_selector_from_name("__execute__"),
            calldata=wrapped_calldata,
            contract_address=self.address,
            signature=[],
            max_fee=tx.max_fee,
            version=tx.version,
        )

    async def _sign_transaction(self, tx: InvokeFunction) -> StarknetTransaction:
        execute_tx = await self._prepare_execute_transaction(tx)
        signature = self.signer.sign_transaction(execute_tx)
        execute_tx = add_signature_to_transaction(execute_tx, signature)
        return execute_tx

    async def add_transaction(
        self,
        transaction: InvokeFunction,
    ) -> SentTransaction:

        if transaction.signature:
            raise TypeError(
                "Adding signatures to a signer tx currently isn't supported"
            )

        return await self.client.add_transaction(
            await self._sign_transaction(transaction)
        )

    async def deploy(self, transaction: Deploy) -> SentTransaction:
        return await self.client.deploy(transaction=transaction)

    async def declare(self, transaction: Declare) -> SentTransaction:
        return await self.client.declare(transaction=transaction)

    async def estimate_fee(
        self,
        tx: InvokeFunction,
        block_hash: Optional[CastableToHash] = None,
        block_number: BlockIdentifier = "pending",
    ) -> int:
        """
        :param tx: Transaction which fee we want to calculate
        :param block_hash: Estimate fee at specific block hash
        :param block_number: Estimate fee at given block number (or "pending" for pending block)
        :return: Estimated fee
        """
        return await self.client.estimate_fee(
            tx=await self._sign_transaction(tx),
            block_hash=block_hash,
            block_number=block_number,
        )

    @staticmethod
    async def create_account(
        client: Client,
        private_key: Optional[int] = None,
        signer: Optional[BaseSigner] = None,
    ) -> "AccountClient":
        """
        Creates the account using
        `OpenZeppelin Account contract
        <https://github.com/starkware-libs/cairo-lang/blob/4e233516f52477ad158bc81a86ec2760471c1b65/src/starkware/starknet/third_party/open_zeppelin/Account.cairo>`_

        :param net: Target net's address or one of "mainnet", "testnet"
        :param chain: Chain used by the network. Required if you use a custom URL for ``net`` param
        :param private_key: Private Key used for the account
        :param signer : Signer used to create account and sign transaction
        :return: Instance of AccountClient which interacts with created account on given network
        """
        if signer is None:
            private_key = private_key or get_random_private_key()

            key_pair = KeyPair.from_private_key(private_key)
            address = await deploy_account_contract(client, key_pair.public_key)
            signer = StarkCurveSigner(
                account_address=address, key_pair=key_pair, chain_id=client.chain
            )
        else:
            address = await deploy_account_contract(client, signer.public_key)

        return AccountClient(
            client=client,
            address=address,
            signer=signer,
        )


async def deploy_account_contract(
    client: Client, public_key: int
) -> AddressRepresentation:
    deploy_tx = make_deploy_tx(
        constructor_calldata=[public_key],
        compiled_contract=COMPILED_ACCOUNT_CONTRACT,
    )
    result = await client.deploy(deploy_tx)
    await client.wait_for_tx(
        tx_hash=result.hash,
    )
    return result.address


def add_signature_to_transaction(
    tx: InvokeFunction, signature: List[int]
) -> InvokeFunction:
    return replace(tx, signature=signature)
