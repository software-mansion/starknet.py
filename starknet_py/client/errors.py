from typing import Optional, Union

from starknet_py.client.http.errors import ClientError
from starknet_py.client.models import AddressRepresentation
from starknet_py.client.models.block import Hash, Tag


class ContractNotFoundError(ClientError):
    """
    Requested contract was not found.
    """

    def __init__(
        self,
        address: AddressRepresentation,
        block_hash: Optional[Hash] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ):
        is_identifier = block_hash is not None or block_number is not None
        identifier = block_hash or block_number
        identifier_name = "block_hash" if block_hash else "block_number"

        message = f"No contract with address {address} found"
        block_info = (
            f" for block with {identifier_name}: {identifier}" if is_identifier else ""
        )
        full_message = message + block_info

        super().__init__(message=full_message)
