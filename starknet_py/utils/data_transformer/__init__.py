import warnings

from starknet_py.utils.data_transformer.data_transformer import FunctionCallSerializer

warnings.warn(
    "Module data_transformer has been deprecated. Use serialization module instead.",
    category=DeprecationWarning,
)
