
cd crypto-cpp
mkdir -p build/Release
sed -i'.original' 's/${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC/-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC ${CMAKE_CXX_FLAGS}/' CMakeLists.txt
(cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="$CMAKE_CXX_COMPILER" -DCMAKE_CXX_FLAGS="$CMAKE_CXX_FLAGS" ../..)
make -C build/Release
cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto