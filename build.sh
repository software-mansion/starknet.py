
cd crypto-cpp
mkdir -p build/Release
(cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="$CMAKE_CXX_COMPILER" ../..)
make -C build/Release
cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto