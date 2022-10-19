import pytest

from starknet_py.net.client_models import Call
from starknet_py.net.client_utils import _invoke_tx_to_call


call = Call(to_addr=1, selector=2, calldata=[3])


@pytest.mark.parametrize(
    "_call, invoke_tx, expected", [(call, None, call), (None, call, call)]
)
def test_invoke_tx_to_call(_call, invoke_tx, expected):
    new_call = _invoke_tx_to_call(call=_call, invoke_tx=invoke_tx)
    assert new_call == expected


def test_invoke_tx_to_call_raises_on_both_provided():
    with pytest.raises(ValueError) as exinfo:
        _invoke_tx_to_call(call=call, invoke_tx=call)

    assert "invoke_tx and call are mutually exclusive" in str(exinfo.value)


def test_invoke_tx_to_call_warns_on_invoke_tx():
    with pytest.warns(DeprecationWarning) as warn:
        _invoke_tx_to_call(invoke_tx=call)

    assert "invoke_tx parameter is deprecated. Use call instead" in str(warn[0].message)
