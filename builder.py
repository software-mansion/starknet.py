import os

from setuptools import Extension
from setuptools.command.build_ext import build_ext


class CryptoExtension(Extension):
    def __init__(self):
        self.name = "crypto_cpp"
        Extension.__init__(self, self.name, sources=[])


class BuildCrypto(build_ext):
    def build_extension(self, ext):
        os.system("""
            cd crypto-cpp
            mkdir -p build/Release
            sed -i'.original' 's/${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC/-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC ${CMAKE_CXX_FLAGS}/' CMakeLists.txt
            (cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="g++" -DCMAKE_CXX_FLAGS="-Wno-type-limits -Wno-range-loop-analysis" ../..)
            make -C build/Release
            cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto
        """)
