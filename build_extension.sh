#!/bin/bash

cd crypto-cpp
mkdir -p build/Release
TARGET_MACHINE=$(gcc -dumpmachine)
echo "Targeting ${TARGET_MACHINE}"
sed -i'.original' "s/\${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC/-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC \${CMAKE_CXX_FLAGS} -target ${TARGET_MACHINE}/" CMakeLists.txt
cat CMakeLists.txt
(cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="g++" -DCMAKE_CXX_FLAGS="-Wno-type-limits -Wno-range-loop-analysis -Wno-unused-parameter" ../..)
make -C build/Release
if [ $? -ne 0 ]; then
  exit 1
fi
cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto
