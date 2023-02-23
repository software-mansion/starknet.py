# pylint: disable=line-too-long
# fmt: off
import pytest
from starkware.starknet.core.os.contract_class.deprecated_class_hash import (
    compute_deprecated_class_hash as sw_compute_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    DeprecatedCompiledClass,
)

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, hash_", [
        ("map_compiled.json", 0x353434f1495ca9a9943cab1c093fb765179163210b8d513613660ff371a5490),
        ("erc20_compiled.json", 0x4923337924bb444be0d227d0976e72b509e1f4e6e25d7aaad7567a23764c9f3),
        ("oz_proxy_compiled.json", 0x104a873052af68063f17239cf1777050c1d0f6ce974cb5e85e9f4ddf8bae5a6),
        ("argent_proxy_compiled.json", 0x59265a4900ee75c3ab641c6df6dd69cf15f1c47ed94be80eb68416947de618a),
        ("universal_deployer_compiled.json", 0x772626159b0f91015d0a91ccf0e48775aa9dbc01a5c717330c61b9767201937),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413c36c287cb410d42f9e531563f68ac60a2913b5053608d640fb9b643acfe6),
    ]
)
def test_compute_class_hash(contract_source, hash_):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    class_hash = compute_class_hash(contract_class)
    sw_class_hash = sw_compute_class_hash(DeprecatedCompiledClass.loads(compiled_contract))
    assert class_hash == hash_ == sw_class_hash
