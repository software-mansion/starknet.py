import pytest

from starknet_py.utils.data_transformer._calldata_reader import (
    CalldataReader,
    OutOfBoundsError,
)


def test_consuming_calldata():
    reader = CalldataReader(list(range(0, 100)))

    assert reader.remaining_len == 100

    assert reader.consume(10) == list(range(0, 10))
    assert reader.remaining_len == 90

    assert reader.consume(5) == list(range(10, 15))
    assert reader.remaining_len == 85

    assert reader.consume(35) == list(range(15, 50))
    assert reader.remaining_len == 50

    with pytest.raises(
        OutOfBoundsError, match="Requested 51 elements, 50 available."
    ) as err_info:
        reader.consume(51)

    assert err_info.value.position == 50
    assert err_info.value.remaining_len == 50
    assert err_info.value.requested_size == 51

    # Nothing was consumed when requested too much above
    assert reader.consume(50) == list(range(50, 100))
    assert reader.remaining_len == 0


def test_empty_calldata():
    reader = CalldataReader([])

    assert reader.remaining_len == 0

    with pytest.raises(
        OutOfBoundsError, match="Requested 10 elements, 0 available."
    ) as err_info:
        reader.consume(10)

    assert err_info.value.position == 0
    assert err_info.value.remaining_len == 0
    assert err_info.value.requested_size == 10
