
cd crypto-cpp
mkdir -p build/Release
export CXXFLAGS="-Wno-type-limits -Wno-range-loop-analysis"
(cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="g++" ../..)
make -C build/Release
if [ $? -ne 0 ]; then
  exit 1
fi
cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto