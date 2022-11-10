import dataclasses
import re
import warnings
from dataclasses import replace
from typing import Optional, List, Union, Dict, Tuple, Iterable

from starkware.crypto.signature.signature import get_random_private_key
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    SentTransactionResponse,
    Hash,
    DeclaredContract,
    Tag,
    TransactionReceipt,
    BlockStateUpdate,
    StarknetBlock,
    Declare,
    Deploy,
    BlockTransactionTraces,
    EstimatedFee,
    Calls,
    TransactionStatus,
    DeployTransactionResponse,
    DeclareTransactionResponse,
    Transaction,
    DeployAccountTransactionResponse,
)
from starknet_py.net.client_utils import _invoke_tx_to_call
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import (
    InvokeFunction,
    StarknetChainId,
    chain_from_network,
)
from starknet_py.net.models.address import AddressRepresentation, parse_address
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.networks import Network, MAINNET, TESTNET
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner, KeyPair
from starknet_py.utils.crypto.facade import Call
from starknet_py.utils.data_transformer.execute_transformer import (
    execute_transformer_by_version,
)
from starknet_py.utils.iterable import ensure_iterable
from starknet_py.utils.sync import add_sync_methods
from starknet_py.utils.typed_data import TypedData as TypedDataDataclass
from starknet_py.net.models.typed_data import TypedData


@add_sync_methods
class AccountClient(Client):
    """
    Extends the functionality of :obj:`Client <starknet_py.net.client.Client>`,
    adding additional methods for creating the account contract.
    """

    # pylint: disable=too-many-public-methods
    def __init__(
        self,
        address: AddressRepresentation,
        client: Client,
        signer: Optional[BaseSigner] = None,
        key_pair: Optional[KeyPair] = None,
        chain: Optional[StarknetChainId] = None,
        supported_tx_version: int = 0,
    ):
        """
        :param address: Address of the account contract
        :param client: Instance of GatewayClient which will be used to add transactions
        :param signer: Custom signer to be used by AccountClient.
                       If none is provided, default
                       :py:class:`starknet_py.net.signer.stark_curve_signer.StarkCurveSigner` is used.
        :param key_pair: Key pair that will be used to create a default `Signer`
        :param chain: ChainId of the chain used to create the default signer
        :param supported_tx_version: Version of transactions supported by account
        """
        # pylint: disable=too-many-arguments
        if chain is None and signer is None:
            raise ValueError("One of chain or signer must be provided")

        self.address = parse_address(address)
        self.client = client

        if signer is None:
            if key_pair is None:
                raise ValueError(
                    "Either a signer or a key_pair must be provided in AccountClient constructor"
                )

            chain = chain_from_network(net=client.net, chain=chain)
            signer = StarkCurveSigner(
                account_address=self.address, key_pair=key_pair, chain_id=chain
            )
        self.signer = signer
        self.supported_tx_version = supported_tx_version

        if self.supported_tx_version == 0:
            warnings.warn(
                "Account supporting transaction version 0 is deprecated. "
                "Use the new account and set supported_tx_version parameter to 1",
                category=DeprecationWarning,
            )

    @property
    def net(self) -> Network:
        return self.client.net

    async def get_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> StarknetBlock:
        return await self.client.get_block(
            block_hash=block_hash, block_number=block_number
        )

    async def get_block_traces(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockTransactionTraces:
        return await self.client.get_block_traces(
            block_hash=block_hash, block_number=block_number
        )

    async def get_state_update(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockStateUpdate:
        return await self.client.get_state_update(
            block_hash=block_hash, block_number=block_number
        )

    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        return await self.client.get_storage_at(
            contract_address=contract_address,
            key=key,
            block_hash=block_hash,
            block_number=block_number,
        )

    async def get_transaction(self, tx_hash: Hash) -> Transaction:
        return await self.client.get_transaction(tx_hash=tx_hash)

    async def get_transaction_receipt(self, tx_hash: Hash) -> TransactionReceipt:
        return await self.client.get_transaction_receipt(tx_hash=tx_hash)

    async def wait_for_tx(
        self,
        tx_hash: Hash,
        wait_for_accept: Optional[bool] = False,
        check_interval=5,
    ) -> Tuple[int, TransactionStatus]:
        return await self.client.wait_for_tx(
            tx_hash=tx_hash,
            wait_for_accept=wait_for_accept,
            check_interval=check_interval,
        )

    async def call_contract(
        self,
        call: Call = None,  # pyright: ignore
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
        *,
        invoke_tx: Call = None,  # pyright: ignore
    ) -> List[int]:
        call = _invoke_tx_to_call(call=call, invoke_tx=invoke_tx)

        return await self.client.call_contract(
            call=call, block_hash=block_hash, block_number=block_number
        )

    async def get_class_hash_at(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        return await self.client.get_class_hash_at(
            contract_address=contract_address,
            block_hash=block_hash,
            block_number=block_number,
        )

    async def get_class_by_hash(self, class_hash: Hash) -> DeclaredContract:
        return await self.client.get_class_by_hash(class_hash=class_hash)

    async def _get_nonce(self) -> int:
        if self.supported_tx_version == 1:
            return await self.get_contract_nonce(self.address, block_hash="latest")

        [nonce] = await self.call_contract(
            Call(
                to_addr=self.address,
                selector=get_selector_from_name("get_nonce"),
                calldata=[],
            ),
            block_hash="pending",
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
            Call(
                to_addr=parse_address(token_address),
                selector=get_selector_from_name("balanceOf"),
                calldata=[self.address],
            ),
            block_hash="pending",
        )

        return (high << 128) + low

    async def prepare_invoke_function(
        self,
        calls: Calls,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        version: Optional[int] = None,
    ) -> InvokeFunction:
        """
        Takes calls and creates InvokeFunction from them

        :param calls: Single call or list of calls
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :param version: Transaction version is supported_tx_version as a default
        :return: InvokeFunction created from the calls (without the signature)

        .. deprecated:: 0.5.0
            This method has been deprecated. Use :meth:`AccountClient.sign_invoke_transaction` to create an already
            signed invoke transactions from calls.
        """
        warnings.warn(
            "prepare_invoke_function has been deprecated. "
            "Use AccountClient.sign_invoke_transaction to create an already signed invoke function.",
            category=DeprecationWarning,
        )

        if version is None:
            version = self.supported_tx_version

        self._assert_version_matches_supported_tx_version(version)

        if version == 0:
            warnings.warn(
                "Transaction with version 0 is deprecated and will be removed in the future. "
                "Use AccountClient supporting the transaction version 1",
                category=DeprecationWarning,
            )

        nonce = await self._get_nonce()

        calldata_py = merge_calls(ensure_iterable(calls))

        if version == 0:
            calldata_py.append(nonce)

        execute_transformer = execute_transformer_by_version(version)
        wrapped_calldata, _ = execute_transformer.from_python(*calldata_py)

        transaction = make_invoke_function_by_version(
            contract_address=self.address,
            calldata=wrapped_calldata,
            signature=[],
            max_fee=0,
            version=version,
            entry_point_selector=get_selector_from_name("__execute__"),
            nonce=None if version == 0 else nonce,
        )

        max_fee = await self._get_max_fee(transaction, max_fee, auto_estimate)

        return dataclasses.replace(transaction, max_fee=max_fee)

    async def _get_max_fee(
        self,
        transaction: Union[InvokeFunction, Declare, DeployAccount],
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> int:
        if auto_estimate and max_fee is not None:
            raise ValueError(
                "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
            )

        if (
            isinstance(transaction, (Declare, DeployAccount))
            and transaction.version != 1
        ):
            raise ValueError(
                "Estimating fee for Declare/DeployAccount transactions with versions other than 1 is not supported."
            )

        if auto_estimate:
            estimate_fee = await self.estimate_fee(transaction)
            max_fee = int(estimate_fee.overall_fee * 1.1)

        if max_fee is None:
            raise ValueError("Max_fee must be specified when invoking a transaction")

        return max_fee

    async def sign_invoke_transaction(
        self,
        calls: Calls,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        version: Optional[int] = None,
    ) -> InvokeFunction:
        """
        Takes calls and creates signed InvokeFunction

        :param calls: Single call or list of calls
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :param version: Transaction version
        :return: InvokeFunction created from the calls
        """
        if version is None:
            version = self.supported_tx_version

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            execute_tx = await self.prepare_invoke_function(
                calls, max_fee, auto_estimate, version
            )

        signature = self.signer.sign_transaction(execute_tx)
        execute_tx = add_signature_to_transaction(execute_tx, signature)

        return execute_tx

    async def sign_declare_transaction(
        self,
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        cairo_path: Optional[List[str]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Declare:
        """
        Create and sign declare transaction.

        Either `compilation_source` or `compiled_contract` is required.

        :param compilation_source: string containing source code or a list of source files paths
        :param compiled_contract: string containing compiled contract bytecode.
                                  Useful for reading compiled contract from a file
        :param cairo_path: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: Signed Declare transaction
        """
        # pylint: disable=too-many-arguments
        if self.supported_tx_version != 1:
            raise ValueError(
                "Signing declare transactions is only supported with transaction version 1"
            )

        compiled_contract = create_compiled_contract(
            compilation_source, compiled_contract, cairo_path
        )
        declare_tx = Declare(
            contract_class=compiled_contract,
            sender_address=self.address,
            max_fee=0,
            signature=[],
            nonce=await self._get_nonce(),
            version=self.supported_tx_version,
        )

        max_fee = await self._get_max_fee(
            transaction=declare_tx, max_fee=max_fee, auto_estimate=auto_estimate
        )
        declare_tx = dataclasses.replace(declare_tx, max_fee=max_fee)
        signature = self.signer.sign_transaction(declare_tx)

        return dataclasses.replace(declare_tx, signature=signature, max_fee=max_fee)

    async def sign_deploy_account_transaction(
        self,
        *,
        class_hash: int,
        contract_address_salt: int,
        constructor_calldata: Optional[List[int]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeployAccount:
        """
        Create and sign deploy account transaction

        :param class_hash: Class hash of the contract class to be deployed
        :param contract_address_salt: A salt used to calculate deployed contract address
        :param constructor_calldata: Calldata to be passed to contract constructor
            and used to calculate deployed contract address
        :param max_fee: Max fee to be paid for deploying account transaction. Enough tokens must be prefunded before
            sending the transaction for it to succeed.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: Signed DeployAccount transaction
        """
        if self.supported_tx_version != 1:
            raise ValueError(
                "Signing deploy account transactions is only supported with transaction version 1"
            )

        constructor_calldata = constructor_calldata or []

        deploy_account_tx = DeployAccount(
            class_hash=class_hash,
            contract_address_salt=contract_address_salt,
            constructor_calldata=constructor_calldata,
            version=self.supported_tx_version,
            max_fee=0,
            signature=[],
            nonce=0,
        )

        max_fee = await self._get_max_fee(
            transaction=deploy_account_tx, max_fee=max_fee, auto_estimate=auto_estimate
        )
        deploy_account_tx = dataclasses.replace(deploy_account_tx, max_fee=max_fee)
        signature = self.signer.sign_transaction(deploy_account_tx)

        return dataclasses.replace(deploy_account_tx, signature=signature)

    async def send_transaction(
        self, transaction: InvokeFunction
    ) -> SentTransactionResponse:
        if transaction.max_fee == 0:
            warnings.warn(
                "Transaction will fail with max_fee set to 0. Change it to a higher value.",
                DeprecationWarning,
            )

        return await self.client.send_transaction(transaction=transaction)

    async def execute(
        self,
        calls: Calls,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        version: Optional[int] = None,
    ) -> SentTransactionResponse:
        """
        Takes calls and executes transaction

        :param calls: Single call or list of calls
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :param version: Transaction version
        :return: SentTransactionResponse
        """
        execute_transaction = await self.sign_invoke_transaction(
            calls, max_fee, auto_estimate, version
        )
        return await self.send_transaction(execute_transaction)

    async def deploy(self, transaction: Deploy) -> DeployTransactionResponse:
        return await self.client.deploy(transaction=transaction)

    async def deploy_account(
        self, transaction: DeployAccount
    ) -> DeployAccountTransactionResponse:
        return await self.client.deploy_account(transaction=transaction)

    async def declare(self, transaction: Declare) -> DeclareTransactionResponse:
        return await self.client.declare(transaction=transaction)

    async def estimate_fee(
        self,
        tx: Union[InvokeFunction, Declare, DeployAccount],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> EstimatedFee:
        """
        :param tx: Transaction which fee we want to calculate
        :param block_hash: Estimate fee at specific block hash
        :param block_number: Estimate fee at given block number (or "pending" for pending block), default is "pending"
        :return: Estimated fee
        """
        signature = self.signer.sign_transaction(tx)
        tx = add_signature_to_transaction(tx, signature)

        return await self.client.estimate_fee(
            tx=tx,
            block_hash=block_hash,
            block_number=block_number,
        )

    async def get_code(self, *args, **kwargs):
        warnings.warn(
            "get_code was removed from Client interface and will be removed from AccountClient in future versions",
            category=DeprecationWarning,
        )
        if not isinstance(self.client, GatewayClient):
            raise TypeError("AccountClient.get_code only supports using GatewayClient")

        return await self.client.get_code(*args, **kwargs)

    def _assert_version_matches_supported_tx_version(self, version: int):
        if version != self.supported_tx_version:
            raise ValueError(
                f"Provided version: {version} is not equal to account's "
                f"supported_tx_version: {self.supported_tx_version}"
            )

    @staticmethod
    async def create_account(
        client: Client,
        private_key: Optional[int] = None,
        signer: Optional[BaseSigner] = None,
        chain: Optional[StarknetChainId] = None,
    ) -> "AccountClient":
        """
        Creates the account using
        `OpenZeppelin Account contract
        <https://github.com/starkware-libs/cairo-lang/blob/4e233516f52477ad158bc81a86ec2760471c1b65/src/starkware/starknet/third_party/open_zeppelin/Account.cairo>`_

        :param client: Instance of Client (i.e. FullNodeClient or GatewayClient)
                       which will be used to add the transactions
        :param private_key: Private Key used for the account
        :param signer: Signer used to create account and sign transaction
        :param chain: ChainId of the chain used to create the default signer
        :return: Instance of AccountClient which interacts with created account on given network

        .. deprecated:: 0.5.0
            This method has been deprecated and will be deleted once transaction version 0 is removed.
            Compiled account contract will no longer be bundled with StarkNet.py.
            Consider transitioning to deploying account contract of choice and creating AccountClient
            through a constructor.
        """
        warnings.warn(
            "Account deployment through AccountClient is deprecated and will be deleted once transaction version "
            "0 is removed. Consider transitioning to creating AccountClient through a constructor.",
            category=DeprecationWarning,
        )

        if chain is None and signer is None:
            raise ValueError("One of chain or signer must be provided")

        if signer is None:
            chain = chain_from_network(net=client.net, chain=chain)
            used_private_key = private_key or get_random_private_key()
            key_pair = KeyPair.from_private_key(used_private_key)
            address = await deploy_account_contract(client, key_pair.public_key)
            signer = StarkCurveSigner(
                account_address=address, key_pair=key_pair, chain_id=chain
            )
        else:
            address = await deploy_account_contract(client, signer.public_key)

        version = get_account_version()

        return AccountClient(
            client=client,
            address=address,
            signer=signer,
            supported_tx_version=version,
        )

    async def get_contract_nonce(
        self,
        contract_address: int,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        return await self.client.get_contract_nonce(
            contract_address, block_hash, block_number
        )

    def sign_message(self, typed_data: TypedData) -> List[int]:
        """
        Sign an TypedData TypedDict for off-chain usage with the starknet private key and return the signature
        This adds a message prefix, so it can't be interchanged with transactions

        :param typed_data: TypedData TypedDict to be signed
        :return: The signature of the TypedData TypedDict
        """
        return self.signer.sign_message(typed_data, self.address)

    def hash_message(self, typed_data: TypedData) -> int:
        """
        Hash a TypedData TypedDict with pedersen hash and return the hash
        This adds a message prefix, so it can't be interchanged with transactions

        :param typed_data: TypedData TypedDict to be hashed
        :return: the hash of the TypedData TypedDict
        """
        typed_data_dataclass: TypedDataDataclass = TypedDataDataclass.from_dict(
            typed_data
        )
        return typed_data_dataclass.message_hash(self.address)

    async def verify_message(self, typed_data: TypedData, signature: List[int]) -> bool:
        """
        Verify a signature of a TypedData TypedDict

        :param typed_data: TypedData TypedDict to be verified
        :param signature: signature of the TypedData TypedDict
        :return: true if the signature is valid, false otherwise
        """
        msg_hash = self.hash_message(typed_data)
        return await self._verify_message_hash(msg_hash, signature)

    async def _verify_message_hash(self, msg_hash: int, signature: List[int]) -> bool:
        """
        Verify a signature of a given hash

        :param msg_hash: hash to be verified
        :param signature: signature of the hash
        :return: true if the signature is valid, false otherwise
        """
        calldata = [msg_hash, len(signature), *signature]

        call = Call(
            to_addr=self.address,
            selector=get_selector_from_name("is_valid_signature"),
            calldata=calldata,
        )
        try:
            await self.call_contract(call=call, block_hash="pending")
            return True
        except ClientError as ex:
            if re.search(r"Signature\s.+,\sis\sinvalid", ex.message):
                return False
            raise ex


async def deploy_account_contract(
    client: Client, public_key: int
) -> AddressRepresentation:
    # pylint: disable=import-outside-toplevel
    # FIXME move this import to top once circular import is resolved
    from starknet_py.transactions.deploy import make_deploy_tx

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        deploy_tx = make_deploy_tx(
            constructor_calldata=[public_key],
            compiled_contract=COMPILED_ACCOUNT_CONTRACT,
        )

    result = await client.deploy(deploy_tx)
    await client.wait_for_tx(
        tx_hash=result.transaction_hash,
    )
    return result.contract_address


def add_signature_to_transaction(
    tx: InvokeFunction, signature: List[int]
) -> InvokeFunction:
    return replace(tx, signature=signature)


def merge_calls(calls: Iterable[Call]) -> List:
    def parse_call(
        call: Call, current_data_len: int, entire_calldata: List
    ) -> Tuple[Dict, int, List]:
        data = {
            "to": call.to_addr,
            "selector": call.selector,
            "data_offset": current_data_len,
            "data_len": len(call.calldata),
        }
        current_data_len += len(call.calldata)
        entire_calldata += call.calldata

        return data, current_data_len, entire_calldata

    calldata = []
    current_data_len = 0
    entire_calldata = []
    for call in calls:
        data, current_data_len, entire_calldata = parse_call(
            call, current_data_len, entire_calldata
        )
        calldata.append(data)

    return [calldata, entire_calldata]


def make_invoke_function_by_version(
    # pylint: disable=too-many-arguments
    contract_address: AddressRepresentation,
    calldata: List[int],
    signature: List[int],
    max_fee: int,
    version: int,
    nonce: Optional[int],
    entry_point_selector: int,
) -> InvokeFunction:
    params = {
        "calldata": calldata,
        "signature": signature,
        "max_fee": max_fee,
        "version": version,
        "nonce": nonce,
        "contract_address": contract_address,
    }

    if version == 0:
        params["entry_point_selector"] = entry_point_selector

    return InvokeFunction(**params)


def get_account_version():
    return 1 if "__validate__" in COMPILED_ACCOUNT_CONTRACT else 0
