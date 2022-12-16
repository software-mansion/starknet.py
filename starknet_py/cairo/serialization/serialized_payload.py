from collections import OrderedDict

from starknet_py.cairo.felt import CairoData


class SerializedPayload(OrderedDict[str, CairoData]):
    """
    Dictionary for serialized payload members. Use ``to_calldata`` to get raw calldata.
    """

    def to_calldata(self) -> CairoData:
        result = []
        for entry_calldata in self.values():
            result.extend(entry_calldata)
        return result
