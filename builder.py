import os

from setuptools import Extension
from setuptools.command.build_ext import build_ext


class CryptoExtension(Extension):
    def __init__(self):
        self.name = "crypto_cpp"
        Extension.__init__(self, self.name, sources=[])


class BuildCrypto(build_ext):
    def build_extension(self, ext):
        os.system(
            """
            cd crypto-cpp
            mkdir -p build/Release
            export CXXFLAGS="-Wno-type-limits -Wno-range-loop-analysis"
            (cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="g++" ../..)
            make -C build/Release
            cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto
        """
        )
